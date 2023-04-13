"""
This is a Python script that serves as a frontend for a conversational AI model built with the `langchain` and `llms` libraries.
The code creates a web application using Streamlit, a Python library for building interactive web apps.
# Author: Avratanu Biswas
# Date: March 11, 2023
"""

# Import necessary libraries
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI

# Initialize llm to None
llm = None

# Set a default value for K
K = 3

# Set Streamlit page configuration
st.set_page_config(page_title='🧠MemoryBot🤖', layout='wide')
# Initialize session states
if "generated" not in st.session_state:
    st.session_state.generated = []

if "past" not in st.session_state:
    st.session_state.past = []

if "input" not in st.session_state:
    st.session_state.input = []  # Change this line

if "stored_session" not in st.session_state:
    st.session_state.stored_session = []

if "users" not in st.session_state:
    st.session_state.users = []

# Check if 'entity_memory' already exists in session_state
# If not, then initialize it
if 'entity_memory' not in st.session_state:
    if llm is not None:
        st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K)
    else:
        st.session_state.entity_memory = None

def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for user_id in range(len(st.session_state["generated"])):
        # Check if the 'generated' and 'past' lists have elements before looping over them
        if st.session_state["generated"][user_id] and st.session_state["past"][user_id]:
            for i in range(len(st.session_state['generated'][user_id])):
                save.append("User " + str(user_id) + ": " + st.session_state["past"][user_id][i])
                save.append("Bot " + str(user_id) + ": " + st.session_state["generated"][user_id][i])

    if save:  # Check if 'save' has elements before appending to 'stored_session'
        st.session_state["stored_session"].append(save)

    st.session_state["generated"] = [[] for _ in st.session_state["users"]]
    st.session_state["past"] = [[] for _ in st.session_state["users"]]
    st.session_state["input"] = [""] * len(st.session_state["users"])

    # Reinitialize the entity_memory object
    st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K)


# Set up sidebar with various options
with st.sidebar.expander("🛠️ ", expanded=False):
    # Option to preview memory store
    if st.checkbox("Preview memory store"):
        with st.expander("Memory-Store", expanded=False):
            st.session_state.entity_memory.store
    # Option to preview memory buffer
    if st.checkbox("Preview memory buffer"):
        with st.expander("Bufffer-Store", expanded=False):
            st.session_state.entity_memory.buffer
    MODEL = st.selectbox(label='Model', options=['gpt-3.5-turbo','text-davinci-003','text-davinci-002','code-davinci-002'])
    K = st.number_input(' (#)Summary of prompts to consider',min_value=3,max_value=1000)

# Set up the Streamlit app layout
st.title("🤖 Chat Bot with 🧠")
st.subheader(" Powered by 🦜 LangChain + OpenAI + Streamlit")

def add_user():
    user_id = len(st.session_state.users)
    st.session_state.users.append(user_id)
    st.session_state.generated.append([])  # Change this line
    st.session_state.past.append([])  # Change this line
    st.session_state.input.append("")  # Change this line
    return user_id


# Define function to remove a user
def remove_user(user_id):
    if user_id in st.session_state.users:
        st.session_state.users.remove(user_id)
        del st.session_state.generated[user_id]
        del st.session_state.past[user_id]
        del st.session_state.input[user_id]

# Define function to get user input
def get_text(user_id):
    input_text = st.text_input(f"User {user_id}: ", st.session_state["input"][user_id], key=f"input_{user_id}",
                            placeholder="Your AI assistant here! Ask me anything ...", 
                            label_visibility='hidden')
    return input_text

# ... (existing code) ...

# Initialize llm to None

# ... other code ...

# Ask the user to enter their OpenAI API key
API_O = st.sidebar.text_input("API-KEY", type="password")

# Session state storage would be ideal
if API_O:
    # Create an OpenAI instance
    llm = OpenAI(temperature=0,
                openai_api_key=API_O, 
                model_name=MODEL, 
                verbose=False)

    # Check if 'entity_memory' already exists in session_state
    # If not, then initialize it
    if 'entity_memory' not in st.session_state or st.session_state.entity_memory is None:
        if llm is not None:
            st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K)
        else:
            st.warning("Please enter the API key to initialize the Conversational AI model.")

    # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
        llm=llm, 
        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        memory=st.session_state.entity_memory
    )
else:
    st.sidebar.warning('API key required to try this app. The API key is not stored in any form.')
    # st.stop()

# Add buttons to add and remove users
with st.sidebar:
    if st.button("Add User"):
        add_user()
    if st.button("Remove User"):
        if st.session_state.users:
            remove_user(st.session_state.users[-1])

# Get the user input for all active users and generate responses
for user_id in st.session_state.users:
    user_input = get_text(user_id)
    if user_input:
        output = Conversation.run(input=user_input)  
        st.session_state.past[user_id].append(user_input)  
        st.session_state.generated[user_id].append(output)


# ... (existing code) ...

# Add a button to start a new chat
st.sidebar.button("New Chat", on_click = new_chat, type='primary')


# Combine the conversation history of all users into a single list
combined_conversations = []
timestamp = 0
for user_id in st.session_state.users:
    for i in range(len(st.session_state['generated'][user_id])):
        combined_conversations.append((user_id, i, "question", timestamp))
        timestamp += 1
        combined_conversations.append((user_id, i, "answer", timestamp))
        timestamp += 1

# Sort the combined list based on the timestamp
sorted_conversations = sorted(combined_conversations, key=lambda x: x[3])

# Display the conversation history using the sorted list
with st.expander("Combined Conversation", expanded=True):
    for user_id, i, msg_type, _ in sorted_conversations:
        if msg_type == "question":
            if i < len(st.session_state['past'][user_id]):
                st.info(f"User {user_id}: {st.session_state['past'][user_id][i]}", icon="🧐")
        else:
            if i < len(st.session_state['generated'][user_id]):
                st.success(f"Bot (for User {user_id}): {st.session_state['generated'][user_id][i]}", icon="🤖")



# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label=f"Conversation-Session:{i}"):
        for j, item in enumerate(sublist):
            if j % 2 == 0:
                st.info(item, icon="🧐")
            else:
                st.success(item, icon="🤖")

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:
    if st.sidebar.button("Clear-all"):
        st.session_state.stored_session = []

