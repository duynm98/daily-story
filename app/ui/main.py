import os
from uuid import uuid4

import streamlit as st

from app import config, save_config
from app.core.generator import generate_video_from_moral

from app import config, load_config


def main():
    global config

    st.set_page_config(layout="wide")  # Set the app to full width
    st.title("Short Story Video Generator")

    # Load the current configuration

    # Create two columns
    col1, col2 = st.columns([0.382, 0.618])

    with col1:
        st.subheader("Configuration")
        # config["app"]["output_folder"] = st.text_input("Output Folder", config["app"]["output_folder"])
        config["story"]["max_words"] = st.number_input("Max Words", value=config["story"]["max_words"], min_value=1)
        config["video"]["language"] = st.selectbox(
            "Video Language", ["Vietnamese", "English"], index=["Vietnamese", "English"].index(config["video"]["language"])
        )
        config["video"]["subtitle_position"] = st.number_input("Subtitle Position", value=config["video"]["subtitle_position"], min_value=0)
        # config["video"]["font_path"] = st.text_input("Font Path", config["video"]["font_path"])
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            config["video"]["font_size"] = st.number_input("Font Size", value=config["video"]["font_size"], min_value=1)
            config["video"]["font_color"] = st.color_picker("Font Color", config["video"]["font_color"])
        with subcol2:
            config["video"]["stroke_width"] = st.number_input("Stroke Width", value=config["video"]["stroke_width"], min_value=0)
            config["video"]["stroke_color"] = st.color_picker("Stroke Color", config["video"]["stroke_color"])
        config["video"]["voice_rate"] = st.number_input("Voice Rate", value=config["video"]["voice_rate"], min_value=0.5, step=0.05)
        # config["video"]["bgm"] = st.text_input("Background Music Path", config["video"]["bgm"])
        config["llm"]["temperature"] = st.number_input("LLM Temperature", value=config["llm"]["temperature"], min_value=0.0, step=0.1)
        # config["telegram"]["bot_token"] = st.text_input("Telegram Bot Token", config["telegram"]["bot_token"])
        # config["telegram"]["chat_id"] = st.text_input("Telegram Chat ID", config["telegram"]["chat_id"])

        if st.button("Save Configuration", use_container_width=True):
            save_config(config)
            st.success("Configuration saved successfully! Rerun the project for the config to take effect.")

    with col2:
        st.subheader("Generate Video")
        # Input field for the user to enter a moral
        moral_text = st.text_area("Enter a moral lesson:", placeholder="E.g., Honesty is the best policy.", max_chars=250).strip()

        button_col = st.columns(1)[0]

        if button_col.button("Generate Video", use_container_width=True, type="primary"):
            if moral_text:
                with st.spinner("Generating video... Please wait."):

                    video_path = generate_video_from_moral(moral_text, str(uuid4()))

                    _, subcol2, _ = st.columns([1, 2, 1])
                    with subcol2:
                        st.video(video_path, format="video/mp4")

            else:
                st.warning("Please enter a moral lesson before generating the video.")


if __name__ == "__main__":
    main()
