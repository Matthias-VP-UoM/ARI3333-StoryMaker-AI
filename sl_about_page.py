import streamlit as st

def about_page():
    st.set_page_config(page_title="About Page", page_icon="🤖")

    #def about_page():
    url_ollama = "https://ollama.com/"
    url_llama_3_2 = "https://ollama.com/library/llama3.2"
    url_hf = "https://huggingface.co/"
    url_flux = "https://huggingface.co/black-forest-labs/FLUX.1-dev"

    st.title("About the Program")

    st.text("StoryMaker AI utilizes advanced AI technology to help you create personalised stories based on your responses.") 
    st.text("It engages your creativity by letting you customise the story to your liking and then dynamically generates a complete story, complete with textual and visual representation, through the use of images.")
    st.text("You can refine the story as you go along, ensuring it fits within your expectations.")

    st.warning("Disclaimer: The stories created by the program are purely fictional and for entertainment purposes, meant to assist with story generation. However, the system may occasionally produce errors or inaccuracies, resulting in unexpected twists or content deviations.")

    #st.caption("Powered by **Ollama** using the **Llama 3.2** model and **Hugging Face** using the **FLUX.1-dev** model.")
    st.caption(f"""
        Powered by <a href="{url_ollama}" target="_blank" class="bold-link"><b>&copy; Ollama</b></a> 
        using the <a href="{url_llama_3_2}" target="_blank" class="bold-link"><b>&copy; Llama 3.2</b></a> model & 
        <a href="{url_hf}" target="_blank" class="bold-link"><b>&copy; Hugging Face</b></a> 
        using the <a href="{url_flux}" target="_blank" class="bold-link"><b>&copy; FLUX.1-dev</b></a> model.
        """,
        unsafe_allow_html=True
    )