# StoryMaker AI

StoryMaker AI is an AI-powered content generation system capable of producing a story which is both creative and fun to read. Featuring a simple to use interface, the platform collects user inputs, generates engaging stories, and creates visuals that reflect the story, offering a seamless and immersive storytelling experience. With features like saving and refining stories, StoryMaker AI empowers users to express their imagination and creativity to bring their ideas to life.

## **How to Use the Application**

## 1. Clone the repository:
The first step is to clone the entire repository, ensuring you have all the available code:

  ```bash
    git clone https://github.com/AFLucas-UOM/Storyboard-AI.git
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

## 3. Create a Hugging Face API key
Go to the <a href="https://huggingface.co/" target="_blank">Hugging Face</a> website and create an account.

Then go to your profile, Settings, and Access Tokens. Follow the steps to create your own Hugging Face API key. Make sure to copy your API key as this will be needed for the next step.

## 4. Add your API key to the project

Go to the working directory where you cloned the repository and create a New Text File. make sure to name it <b>config.ini</b>.

On the first line of the new config file, write <b>[HuggingFace</b>.<br>
On the second line, write the following line, where "xxx" represents the part of your API key that comes after the prefix "hf_":

```bash
    api_key = hf_xxx
  ```

## 5. Start the App
  ```bash
  streamlit run sl_story_gen.py
  ```

## Note
This was developed for the <b><i>ARI3333</i></b> study unit, which is titled <b><i>"Generative AI"</i></b>
