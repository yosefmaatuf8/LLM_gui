import gradio as gr
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os
import torch
import nltk
from nltk.tokenize import sent_tokenize

from backend import *

def remove_paragraphs(text):
   return text.replace("\n", " ")

def copy_last_response(history):
    if history:
        last_response = history[-1][1]
        last_response = last_response.replace('<div style="text-align: left; direction: ltr;">', '').replace('</div>', '')
        last_response = last_response.replace('<p style="text-align: left; direction: ltr;">', '').replace('</p>', '')
        last_response = last_response.replace('\n', ' ')
        return last_response
    else:
        return ""

def create_paragraphs(bot_response, sentences_per_paragraph=4):
   sentences = "hello"#sent_tokenize(bot_response)
   paragraphs = []
   current_paragraph = ""

   for i, sentence in enumerate(sentences, start=1):
       current_paragraph += " " + sentence
       if i % sentences_per_paragraph == 0:
           paragraphs.append(current_paragraph.strip())
           current_paragraph = ""

   if current_paragraph:
       paragraphs.append(current_paragraph.strip())

   formatted_paragraphs = "\n".join([f'<p style="text-align: left; direction: ltr;">{p}</p>' for p in paragraphs])
   return formatted_paragraphs



def chat(input_text, history, max_new_tokens, min_length, no_repeat_ngram_size, num_beams, early_stopping, temperature, top_p, top_k, create_paragraphs_enabled):
   user_input = f'<div style="text-align: left; direction: ltr;">{input_text}</div>'
   response = generate_response(input_text, max_new_tokens, min_length, no_repeat_ngram_size, num_beams, early_stopping, temperature, top_p, top_k)

   if create_paragraphs_enabled:
       response = create_paragraphs(response)

   bot_response = f'<div style="text-align: left; direction: ltr;">{response}</div>'
   history.append((user_input, bot_response))

   return history, history, input_text

def update_model(selected_model):
   global model_name
   model_name = selected_model


with gr.Blocks() as demo:
   gr.Markdown("# LLM_gui", elem_id="title")
   gr.Markdown("hi there", elem_id="subtitle")


   with gr.Accordion("Adjustments", open=False):

       model_selector = gr.Dropdown(
           choices=models_names,
           label="Select Model",
           value=model_name  # Default value
       )
       gr.Button("change model").click(
           update_model,  # Function to call
           inputs=model_selector,  # Input from dropdown
       )

       with gr.Row():
           with gr.Column(): # left
               max_new_tokens = gr.Slider(minimum=10, maximum=1500, value=100, step=10, label="Max New Tokens")
               min_length = gr.Slider(minimum=10, maximum=300, value=100, step=10, label="Min Length")
               no_repeat_ngram_size = gr.Slider(minimum=1, maximum=6, value=4, step=1, label="No Repeat N-Gram Size")
           with gr.Column(): # right
               num_beams = gr.Slider(minimum=1, maximum=16, value=4, step=1, label="Num Beams")
               temperature = gr.Slider(minimum=0.1, maximum=2.0, value=0.2, step=0.1, label="Temperature")
               top_p = gr.Slider(minimum=0.1, maximum=1.0, value=0.7, step=0.1, label="Top P")
               top_k = gr.Slider(minimum=1, maximum=100, value=30, step=1, label="Top K")
       early_stopping = gr.Checkbox(value=True, label="Early Stopping")


   with gr.Row():
       message = gr.Textbox(placeholder="Type your message...", label="User messege", elem_id="message", scale=4)
       prompt = gr.Textbox(placeholder="Type your prompt...", label="prompt", elem_id="prompt", scale=4)
       submit = gr.Button("Send", scale=1)

   with gr.Row():
       create_paragraphs_checkbox = gr.Checkbox(label="Create Paragraphs", value=False)
       remove_paragraphs_btn = gr.Button("Remove Paragraphs")
       copy_last_btn = gr.Button("Copy Last Response")

   chatbot = gr.Chatbot(elem_id="chatbot")


   submit.click(chat, inputs=[message, chatbot, max_new_tokens, min_length, no_repeat_ngram_size, num_beams, early_stopping, temperature, top_p, top_k, create_paragraphs_checkbox], outputs=[chatbot, chatbot, message])
   remove_paragraphs_btn.click(remove_paragraphs, inputs=message, outputs=message)
   copy_last_btn.click(copy_last_response, inputs=chatbot, outputs=message)
   
   demo.css = """
       #message, #message * {
           text-align: left !important;
           direction: ltr !important;
       }
       
       #chatbot, #chatbot * {
           text-align: left !important;
           direction: ltr !important;
       }
       
       #title, .label {
           text-align: left !important;
       }
       
       #subtitle {
           text-align: left !important;
       }
   """

demo.launch()