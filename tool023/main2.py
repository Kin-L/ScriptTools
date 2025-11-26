import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from matplotlib.colors import LinearSegmentedColormap
import subprocess
from concurrent.futures import ThreadPoolExecutor

DEFAULT_CONFIG = {
    "fft_size": 2048,
    "sample_rate": 44100,
    "min_decibels": -100,
    "max_decibels": -12,
    "smoothing_time_constant": 0.5,
    "min_frequency": 0,
    "max_frequency": 2500,
    "width": 854,
    "height": 480,
    "bar_spacing": 1,
    "color": ["#775FD8", "#B6AAFF"],
    "background_color": "#121212",
    "frame_skip": 1,
    "workers": 4
}


def generate_spectrum_video(flac_path, output_path, config=None):
    config = {**DEFAULT_CONFIG, **(config or {})}

    # 加载音频文件
    print("加载音频文件...")
    y, sr = librosa.load(flac_path, sr=config["sample_rate"])

    with tempfile.TemporaryDirectory() as temp_dir:
        print("生成频谱帧...")

        # 配置matplotlib
        plt.style.use('dark_background')
        plt.ioff()  # 关闭交互模式
        fig, ax = plt.subplots(
            figsize=(config["width"] / 100, config["height"] / 100),
            dpi=100
        )
        fig.patch.set_facecolor(config["background_color"])
        ax.set_facecolor(config["background_color"])
        ax.set_xlim(0, config["width"])
        ax.set_ylim(0, config["height"])
        ax.axis('off')

        # 创建渐变色映射
        cmap = LinearSegmentedColormap.from_list("spectrum_cmap", config["color"])

        # 计算STFT
        n_fft = config["fft_size"]
        hop_length = n_fft // 4
        stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
        stft_db = librosa.amplitude_to_db(abs(stft))

        # 频率过滤
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        freq_mask = (frequencies >= config["min_frequency"]) & (frequencies <= config["max_frequency"])
        filtered_stft = stft_db[freq_mask, :]
        num_bins = filtered_stft.shape[0]  # 获取实际频率 bin 数量

        # 标准化分贝值
        filtered_stft = np.clip(
            (filtered_stft - config["min_decibels"]) /
            (config["max_decibels"] - config["min_decibels"]),
            0, 1
        )

        # 修复平滑算法（使用正确的向量化实现）
        if config["smoothing_time_constant"] > 0:
            alpha = config["smoothing_time_constant"]
            smoothed = np.zeros_like(filtered_stft)
            smoothed[:, 0] = filtered_stft[:, 0]
            for i in range(1, filtered_stft.shape[1]):
                smoothed[:, i] = alpha * smoothed[:, i - 1] + (1 - alpha) * filtered_stft[:, i]
            filtered_stft = smoothed

        # 计算跳帧后的索引
        total_frames = filtered_stft.shape[1]
        frame_indices = np.arange(0, total_frames, config["frame_skip"])
        effective_fps = (sr / hop_length) / config["frame_skip"]
        print(f"优化后总帧数: {len(frame_indices)} (原始: {total_frames})")

        # 计算柱形参数（确保与频率 bin 数量匹配）
        bar_width = (config["width"] - (num_bins * config["bar_spacing"])) / num_bins
        x_positions = np.arange(num_bins) * (bar_width + config["bar_spacing"])

        # 预计算高度和颜色
        heights_all = filtered_stft * config["height"]
        colors_all = cmap(filtered_stft)

        # 并行生成帧（每个线程使用独立的轴对象避免冲突）
        def save_frame(t_idx):
            # 为每个线程创建独立的图像对象
            fig_thread, ax_thread = plt.subplots(
                figsize=(config["width"] / 100, config["height"] / 100),
                dpi=100
            )
            fig_thread.patch.set_facecolor(config["background_color"])
            ax_thread.set_facecolor(config["background_color"])
            ax_thread.set_xlim(0, config["width"])
            ax_thread.set_ylim(0, config["height"])
            ax_thread.axis('off')

            t = frame_indices[t_idx]
            # 确保索引不越界
            if t >= heights_all.shape[1]:
                t = heights_all.shape[1] - 1

            # 绘制柱状图（确保x和height长度一致）
            bars = ax_thread.bar(
                x_positions,
                heights_all[:, t],
                width=bar_width,
                color=colors_all[:, t]
            )

            frame_file = os.path.join(temp_dir, f"frame_{t_idx:05d}.png")
            plt.savefig(frame_file, bbox_inches='tight', pad_inches=0)
            plt.close(fig_thread)  # 关闭当前线程的图像，释放内存
            return t_idx

        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=config["workers"]) as executor:
            futures = [executor.submit(save_frame, i) for i in range(len(frame_indices))]

            for i, future in enumerate(futures):
                try:
                    future.result()
                    if i % 100 == 0:
                        print(f"已生成 {i}/{len(frame_indices)} 帧")
                except Exception as e:
                    print(f"生成帧 {i} 时出错: {str(e)}")

        plt.close(fig)

        # 合并音频和视频
        print("合并音频和视频...")
        audio_temp = os.path.join(temp_dir, "audio.aac")

        subprocess.run([
            "ffmpeg", "-y", "-i", flac_path,
            "-c:a", "aac", "-b:a", "192k", "-loglevel", "error",
            audio_temp
        ], check=True)

        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(effective_fps),
            "-i", os.path.join(temp_dir, "frame_%05d.png"),
            "-i", audio_temp,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", 23,
            "-threads", str(config["workers"]),
            "-c:a", "copy", "-shortest", "-loglevel", "error",
            output_path
        ], check=True)

    print(f"视频已保存至: {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("用法: python spectrum_generator.py <输入FLAC文件> <输出视频文件>")
        sys.exit(1)

    input_flac = sys.argv[1]
    output_video = sys.argv[2]

    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("错误: 未找到FFmpeg。请安装FFmpeg并确保它在系统PATH中。")
        sys.exit(1)

    generate_spectrum_video(input_flac, output_video)