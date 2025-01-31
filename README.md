# StoryMaker AI

StoryMaker AI is an AI-powered content generation system capable of producing a story which is both creative and fun to read. Featuring a simple to use interface, the platform collects user inputs, generates engaging stories, and creates visuals that reflect the story, offering a seamless and immersive storytelling experience. With features like saving and refining stories, StoryMaker AI empowers users to express their imagination and creativity to bring their ideas to life.

## Video

[Click here to watch the demo video](https://drive.google.com/file/d/174hbLNTL6IWvkWrUd_o3WF-hRcwwY0ks/view?usp=sharing)

## **How to Use the Application**

## 1. Clone the repository:
The first step is to clone the entire repository, ensuring you have all the available code:

```bash
git clone https://github.com/Matthias-VP-UoM/ARI3333-StoryMaker-AI.git
```

## 2. Install package dependencies
In order to install the package dependencies, you must ensure that Python and pip are installed on your device.
Then, perform one of the following techniques to get the necessary packages:

### a. Install the packages from requirements.txt

```bash
pip install -r requirements.txt
```

### b. Install the Streamlit and Ollama packages separately, which will automatically install the latest version of the rest of the packages

```bash
pip install streamlit
```

```bash
pip install ollama
```

## 3. Install Ollama
Although this project can work without performing this step, it is still imperative that you ensure that both Ollama and the necessary models are installed.

To install Ollama, go to the <a href="https://ollama.com/" target="_blank">Ollama Home Page</a> and download the latest version of Ollama available for your operating system.

Once Ollama is fully installed, go to a Command Line, and type the following 2 commands to install the following 2 models:

```bash
ollama pull llama3.2
```

```bash
ollama pull llama-guard3:1b
```


Once the above two processes are complete, you can check that both of them are installed by using the following command:

```bash
ollama list
```

## 4. Create a Hugging Face API key
For safety purposes, the API key used to access the FLUX.1-dev model is not provided in this repository. Therefore, you will have to create your own key.

First, go to the <a href="https://huggingface.co/" target="_blank">Hugging Face</a> website and create an account.

Then go to your profile, Settings, and Access Tokens. Follow the steps to create your own Hugging Face API key. Make sure to copy your API key as this will be needed for the next step.

## 5. Add your API key to the project

Go to the working directory where you cloned the repository and create a New Text File. make sure to name it <b>config.ini</b>.

On the new config file, write the following 2 lines, where "xxx" represents the part of your API key that comes after the prefix "hf_":

```bash
[HuggingFace]
api_key = hf_xxx
```

## 6. Start the App
```bash
streamlit run sl_story_gen.py
```

## Note
This was developed for the <b><i>ARI3333</i></b> study unit, which is titled <b><i>"Generative AI"</i></b>
