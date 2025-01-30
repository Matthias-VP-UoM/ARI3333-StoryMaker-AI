import streamlit as st
import ollama
import datetime
import os
import json
import re
from pathlib import Path
from pdf_class import PDF
from image_gen_func import generate_images, extract_image_prompts, generate_image_prompts, generate_image_prompts_2, load_image_model
from sl_about_page import about_page

def count_paragraphs(story_text):
    # Split the story_text by double newline characters
    paragraphs = story_text.split("\n\n")
    # Filter out any empty strings (if there are any)
    paragraphs = [p for p in paragraphs if p.strip()]
    # Return the number of paragraphs
    return len(paragraphs), paragraphs

def extract_story_elements(story_text):
    paras_prompt = f"""
    From the given story below, please extract the paragraphs which state the beginning, climax, and end of the story:
    {story_text}
    """

    response = ollama.chat(
        model='llama3.2',
        messages=[
            {"role": "user", "content": paras_prompt}
        ]
    )

    paras_text = response['message']['content']

    # Regular expression to match paragraphs following the headings
    paragraphs = re.findall(r'\*\*.*?\*\*([\s\S]*?)(?=\n\*\*|$)', paras_text)

    # Remove leading/trailing whitespace and print each extracted paragraph
    cleaned_paragraphs = [paragraph.strip() for paragraph in paragraphs]

    paras_dict = {"begin": cleaned_paragraphs[0], "climax": cleaned_paragraphs[1], "end": cleaned_paragraphs[2]}

    #for element, para in paras_dict.items():
        #print(f"{element.capitalize()}:\n{para}\n")
    
    return paras_dict


def verify_content(story_content):
    response = ollama.chat(
        model='llama-guard3:1b',
        messages=[
            {"role": "user", "content": story_content}
        ]
    )

    if response['message']['content'] == "safe":
        #print("Transfer to other model")
        return True, response
    else:
        #print(response['message']['content'])
        return False, response

def save_chat_history(chat_file):
    downloads_folder = Path.home() / "Downloads"

    chat_file_path = os.path.join(downloads_folder, chat_file)

    with open(chat_file_path, 'w') as file:
        json.dump(st.session_state.messages, file, indent=4)
    st.success(f"Story saved to {chat_file} in the Downloads folder!")

def save_to_pdf(story):
    story_title = story.split('**')[1]
    story_content = str(story.split('**')[2]).lstrip('\n')

    downloads_folder = Path.home() / "Downloads"

    pdf = PDF()
    pdf.set_title(story_title)
    pdf.print_chapter(story_content.replace('–', '-'))

    if "gen_imgs_list" in st.session_state:
        for idx, img_path in enumerate(st.session_state.gen_imgs_list):
            pdf.add_page()  # Add a new page for each image
            img_h = pdf.h - 115

            pdf.image(img_path, x=10, y=50, w=190)  # Adjust x, y, width, and height as needed

            pdf.set_y(50 + img_h + 10)  # Position cursor for caption (adjust Y value based on image size)
            pdf.set_font("Times", size=12)
            pdf.multi_cell(0, 10, f"Figure {idx + 1}: {st.session_state.gen_imgs_prompts_list[idx]}", align="C")


    pdf.output(os.path.join(downloads_folder, f"{story_title}.pdf"))

    st.success(f"Story downloaded to the Downloads folder as {story_title}!")

def get_safety_type(safety_response):
    if 'S1' in safety_response:
        return "Violent Crimes"
    elif 'S2' in safety_response:
        return "Non-Violent Crimes"
    elif 'S3' in safety_response:
        return 'Sexual Crimes'
    elif 'S4' in safety_response:
        return 'Crimes involving Children'
    elif 'S5' in safety_response:
        return 'Defamation'
    elif 'S6' in safety_response:
        return 'Specialized Advice'
    elif 'S7' in safety_response:
        return 'Privacy'
    elif 'S8' in safety_response:
        return 'Intellectual Property'
    elif 'S9' in safety_response:
        return 'Indiscriminate Weapons'
    elif 'S10' in safety_response:
        return 'Hate'
    elif 'S11' in safety_response:
        return 'Suicide/Self-Harm'
    elif 'S12' in safety_response:
        return 'Sexual Content'
    elif 'S13' in safety_response:
        return 'Elections'
    else:
        return ""

# Takes in parameters from user and generates a prompt which is used to create a story
def generate_story(theme, setting, tone, audience, characters, story_length):
    # Prepare the prompt for the model
    character_descriptions = ""
    for index, character in enumerate(characters):
        character_descriptions += f"""
        Character {index+1}:
        Name: {character['name']}
        Description: {character['desc']}
        Role: {character['role']}

        """
    
    audience_stmt = ""
        
    if audience == "Under 5":
        audience_stmt = "children under the age of 5"
    elif audience == "5-12":
        audience_stmt = "children between the age of 5 and 12 years old"
    elif audience == "13-18":
        audience_stmt = "teenagers between the age of 13 and 18 years old"
    elif audience == "Over 18":
        audience_stmt = "adults over the age of 18"
    else:
        audience_stmt = "people of all ages"
    
    story_stmt = str(story_length).lower()
    
    
    prompt = f"""
    Generate a {story_stmt} story that is suitable for {audience_stmt} given the following information along with the title of the story, while ensuring that the story story_text is coherent, with a structured narrative. Please place the story title between ** ** characters:
    Theme: {theme}
    Setting: {setting}
    Tone: {tone}
    Information about the Characters to be included:
    {character_descriptions}
    """

    prompt_cleaned = '\n'.join(line.lstrip() for line in prompt.splitlines())

    safe_prompt, prompt_resp = verify_content(prompt_cleaned)

    prompt_safety_label = get_safety_type(prompt_resp['message']['content'])

    if not safe_prompt:
        return f"Please update your prompts to ensure safety guidelines, as your entered parameters contain the following hazard: {prompt_safety_label}\n"

    # Call the Ollama API using the ollama library
    #response = ollama.generate(model=st.session_state['ollama_model'], prompt=prompt)
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': prompt_cleaned,
        },
    ])

    if response.get("message"):
        story = response["message"]['content']
        #print(story)
        try:
            story_title = story.split('**')[1]
            story_content = str(story.split('**')[2]).lstrip('\n')

            safe_content, prompt_story = verify_content(story_content)

            story_safety_label = get_safety_type(prompt_story['message']['content'])

            if safe_content:
                st.session_state.messages.append({"role": "user", "content": prompt_cleaned})
                st.session_state.messages.append({"role": "assistant", "content": response["message"]['content']})
                return story
            else:
                return f"The story contains elements that need review for ethical practices. This was the ethical hazard produced: {story_safety_label}."
        except:
            return "An error occurred during story generation."
    else:
        return "Error: Unable to generate story."

def refine_story(story_title, story_content, refinements):
    refinement_prompt = f"""
    The user has requested modifications to the story titled "{story_title}". Below are the details of the requested changes:
    - **Part to Adjust**: {refinements['part_to_adjust']}
    {f"- **Paragraph Text**: {refinements['paragraph_text']}" if refinements['paragraph_text'] else ""}
    - **Type of Adjustment**: {refinements['adjustment_type']}
    
    ### Details of the Adjustments:
    {f"- New Length: {refinements['details']['new_length']}" if refinements['details']['new_length'] else ""}
    {f"- Style Refinement: {refinements['details']['style_refinement']}" if refinements['details']['style_refinement'] else ""}
    {f"- Plot Refinement: {refinements['details']['plot_refinement']}" if refinements['details']['plot_refinement'] else ""}
    {f"- Character Modifications: {refinements['details']['character_modification']}" if refinements['details']['character_modification'] else ""}
    
    {f"### Additional Comments:" if refinements['additional_comments'] else ""}
    {refinements['additional_comments']}

    Please generate the refined {"paragraph" if refinements['paragraph_text'] else "story"} given the above details while maintaining coherence, structure, and flow{", and place the story title between ** ** characters." if not refinements['paragraph_text'] else "."}
    """

    # Clean up the prompt
    prompt_cleaned = '\n'.join(line.lstrip() for line in refinement_prompt.splitlines())

    # Call the Ollama API for refinement
    response = ollama.chat(
        model='llama3.2',
        messages=[
            {'role': 'user', 'content': prompt_cleaned}
        ]
    )

    # Handle response
    if response.get("message"):
        refined_story = response["message"]['content']
        try:
            # Verify content safety
            num_paras, paras_text = count_paragraphs(refined_story)
            if num_paras > 1:
                refined_story_title = refined_story.split('**')[1]
                refined_story_content = refined_story.split('**', 2)[-1].strip()
            else:
                refined_story_content = paras_text[0]
            safe_content, prompt_story = verify_content(refined_story_content)

            story_safety_label = get_safety_type(prompt_story['message']['content'])

            if safe_content:
                st.session_state.messages.append({"role": "user", "content": prompt_cleaned})
                st.session_state.messages.append({"role": "assistant", "content": refined_story})
                return refined_story
            else:
                return f"The refined story contains elements that need review for ethical practices. This was the ethical hazard produced: {story_safety_label}."
        except:
            return "An error occurred during refinement."
    else:
        return "Error: Unable to refine the story."

def set_story_parameters(theme, setting, tone, audience_type, characters_list, story_length):
    st.session_state["story_params"]['theme'] = theme
    st.session_state["story_params"]['setting'] = setting
    st.session_state["story_params"]['tone'] = tone
    st.session_state["story_params"]['audience_type'] = audience_type
    st.session_state["story_params"]['characters_list'] = characters_list
    st.session_state["story_params"]['story_length'] = story_length

# Streamlit UI
def main():
    st.set_page_config(page_title="StoryMaker AI", page_icon="🤖")

    st.title("StoryMaker AI")
    st.subheader("Create and build your own stories using your imagination!")

    chat_folder = "chat_history"

    today_date = datetime.datetime.now()
    chat_dt_name = datetime.datetime.strftime(today_date, ("%Y-%m-%d_%H-%M-%S"))
    chat_file_name = f'{chat_dt_name}.json'
    
    chat_session_file = os.path.join(chat_folder, chat_file_name)

    if "ollama_model" not in st.session_state:
        st.session_state["ollama_model"] = "llama3.2"
    
    if "story_params" not in st.session_state:
        st.session_state["story_params"] = {"theme": "", "setting": "", "tone": "", "audience_type": "", "story_length": "", "characters_list": []}
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "feedback_open" not in st.session_state:
        st.session_state.feedback_open = False
    
    if "requested_changes" not in st.session_state:
        st.session_state.requested_changes = ""
    
    if "story_refined" not in st.session_state:
        st.session_state.story_refined = False
    
    if "gen_imgs_list" not in st.session_state:
        st.session_state.gen_imgs_list = []
    
    if "gen_imgs_prompts_list" not in st.session_state:
        st.session_state.gen_imgs_prompts_list = []
    
    if "imgs_generated" not in st.session_state:
        st.session_state.imgs_generated = False

    # Inputs for theme and setting
    
    theme_options = ["Adventure", "Sci-Fi", "Mystery", "Comedy", "Fantasy", "Survival", "Love", "Good vs Evil", "Friendship", "Family", "Loss and Grief"]
    theme = st.selectbox("Enter the theme of your story:", theme_options)
    setting = st.text_input("Enter the setting of your story:", placeholder="e.g. A mysterious island in the middle of the ocean, A distant galaxy, Ancient ruins")
    tone = st.selectbox("Enter the tone of your story:", ['suspenseful', 'homorous', 'thrilling', 'passionate', 'inspiring', 'mysterious', 'sarcastic', 'motivational'])
    audience_type = st.selectbox("Select the age group of the audience that you want the story to be focused on:", ["All Ages", "Under 5", "5-12", "13-18", "Over 18"])
    story_length = st.selectbox("Select how long you want the story to be:", ["Short", "Medium", "Long"])

    # Input for characters
    st.write("### Character Customization:")
    character_count = st.number_input("How many characters?", min_value=1, max_value=10, step=1)
    characters_list = []
    characters = {}
    for i in range(character_count):
        name = st.text_input(f"Character {i + 1} Name:")
        description = st.text_area(f"Character {i + 1} Description:")
        role = st.text_area(f"Character {i + 1} Role in Story:")
        if name and description and role:
            characters["name"] = name
            characters["desc"] = description
            characters["role"] = role
            characters_list.append(characters)
        st.divider()

    # Generate story button
    if st.button("Generate Story"):
        if not theme or not setting or not characters or not tone or not audience_type or not story_length:
            st.error("Please provide all required details (theme, setting, tone, audience type, story length, and characters).")
        else:
            set_story_parameters(theme, setting, tone, audience_type, characters_list, story_length)
            with st.spinner("Generating your story..."):
                story = generate_story(st.session_state["story_params"]['theme'], st.session_state["story_params"]['setting'], st.session_state["story_params"]['tone'], st.session_state["story_params"]['audience_type'], st.session_state["story_params"]['characters_list'], st.session_state["story_params"]['story_length'])
            if len(story) > 200:
                st.session_state["error_msg"] = ""
                st.session_state["story_text"] = story
            else:
                st.session_state["error_msg"] = story
    
    # Display the story if it exists in the session state
    if "story_text" in st.session_state and st.session_state["story_text"]:
        if not st.session_state.story_refined:
            st.success("Here is your story:")
        else:
            st.success("Here is your refined story:")
        st.write(st.session_state["story_text"])

        # Generate images button
        if st.button("Generate Story Images"):
            try:
                img_model = load_image_model()
                images_list = []
                images_prompts_list = []
                with st.spinner("Generating story images...\nThis might take 10 to 15 minutes!"):
                    images_prompts_text = generate_image_prompts_2(st.session_state["story_text"])
                    images_prompts_list = extract_image_prompts(images_prompts_text)
                    images_list = [generate_images(image_prompt, img_model) for image_prompt in images_prompts_list]
                
                st.session_state.gen_imgs_list = images_list.copy()
                st.session_state.gen_imgs_prompts_list = images_prompts_list.copy()
                
            except:
                st.session_state.gen_imgs_list.clear()
                st.session_state.gen_imgs_prompts_list.clear()
                st.error("An unexpected error happened whilst generating images! Please try again!")

        if len(st.session_state.gen_imgs_list) > 0:
            st.success("Here are your images!")
            for i in range(len(st.session_state.gen_imgs_list)):
                st.image(st.session_state.gen_imgs_list[i], caption=st.session_state.gen_imgs_prompts_list[i])
        
        # Save prompts & responses button
        if st.button("Save Program Interactions"):
            save_chat_history(chat_file_name)
        
        # Download story to PDF button
        if st.button("Download Story"):
            save_to_pdf(st.session_state["story_text"])
        
        # User feedback & refinement button
        if st.button("Adjust Story"):
            st.session_state.feedback_open = True
        
        if st.session_state.feedback_open:          
            part_to_adjust = st.selectbox("Do you want to adjust the whole story or just a specific paragraph of the story:", ["The Whole Story", "A Specific Paragraph"])

            # ["Continue the story", "Change the tone", "Modify specific paragraph", "Modify characters"]

            if part_to_adjust == "A Specific Paragraph":
                num_paras, paras_text = count_paragraphs(st.session_state["story_text"])
                para_choice = [f"Paragraph {count+1}" for count in range(num_paras)]
                para_num = st.selectbox("Choose which paragraph you would like to modify:", para_choice)
                para_text = paras_text[int(para_num.split()[1])-1]
            
            
            adjustment_type = st.selectbox("Select the adjustment you would like to make:", ["Modify Length of Selected Part", "Refine Style", "Modify Characters", "Modify Plot"])

            if adjustment_type == "Modify Length of Selected Part":
                story_new_length = st.selectbox("Select length of new story:", ['Much Shorter', 'Slightly Shorter', 'Slightly Longer', 'Much Longer'])
            elif adjustment_type == "Modify Characters":
                character_new = {}
                character_old = {}
                char_num_choice = [int(idx+1) for idx in range(len(st.session_state["story_params"]['characters_list']))]
                char_num = st.selectbox("Choose the character you wish to modify:", char_num_choice)

                if char_num != None:
                    character_old = st.session_state["story_params"]['characters_list'][char_num-1]
                    name = st.text_input(f"Character Name:", value=character_old['name'])
                    description = st.text_area(f"Character Description:", value=character_old['desc'])
                    role = st.text_area(f"Character Role in Story:", value=character_old['role'])
                    if name and description and role:
                        character_new["name"] = name
                        character_new["desc"] = description
                        character_new["role"] = role
            elif adjustment_type == "Refine Style":
                style_refinement = st.selectbox("What would you like to refine:", ['More Dialogue', 'More Action', 'More Descriptive', 'Adjust Language Complexity'])
            elif adjustment_type == "Modify Plot":
                plot_refinement = st.selectbox("What would you like to change about the plot:", ["Change Pacing", "Modify Conflict", "Modify Ending", "Add Plot Twist"])
            
            feedback_comment = st.text_area("State any additional details regarding your selected changes:")

            refinements = {
                "part_to_adjust": part_to_adjust,
                "paragraph_text": para_text if part_to_adjust == "A Specific Paragraph" else None,
                "adjustment_type": adjustment_type,
                "details": {
                    "new_length": story_new_length if adjustment_type == "Modify Length of Selected Part" else None,
                    "style_refinement": style_refinement if adjustment_type == "Refine Style" else None,
                    "plot_refinement": plot_refinement if adjustment_type == "Modify Plot" else None,
                    "character_modification": character_new if adjustment_type == "Modify Characters" else None,
                },
                "additional_comments": feedback_comment
            }

            st.divider()

            if st.button("Generate Modified Story"):
                if not adjustment_type:
                    st.error("Please provide an adjustment you want to make to the story.")
                else:
                    with st.spinner("Refining the story..."):
                        refined_story = refine_story(
                            story_title=st.session_state["story_text"].split('**')[1],
                            story_content=st.session_state["story_text"],
                            refinements=refinements
                        )
                    
                    refined_num, _ = count_paragraphs(refined_story)
                    if len(refined_story) > 200 or refined_num == 1:
                        num_paras_new, paras_text_new = count_paragraphs(refined_story)                          
                        st.session_state["story_refined"] = True
                        st.session_state["error_msg"] = ""
                        if num_paras_new > 1:
                            st.session_state["story_text"] = refined_story
                        else:
                            st.session_state["story_text"] = st.session_state["story_text"].replace(refinements['paragraph_text'], paras_text_new[0])
                        st.rerun()
                    else:
                        st.session_state["error_msg"] = refined_story
        
        if st.session_state["story_refined"]:
            st.success("Your story has been refined! You can find it above!")
                
    elif "error_msg" in st.session_state and st.session_state["error_msg"] != "":
        st.error(st.session_state["error_msg"])
    
    st.warning("Please note that content generated by the program may not fully align with your vision!")
            


if __name__ == "__main__":
    pg = st.navigation([
        st.Page(main, title="Create your Own Story"),
        st.Page(about_page, title="About Page"),
    ])
    pg.run()
    #main()
