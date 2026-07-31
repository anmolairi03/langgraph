import streamlit as st
from backend import bot, retrieve_all_threads, chat_name_llm
from langchain_core.messages import HumanMessage
import uuid

################################## utility funcs ##########################################

def get_thread_id():
    return uuid.uuid4()


def generate_chat_name(message):
    response = chat_name_llm.invoke(
        f"Generate a short name for this chat based on the user's message:\n{message}"
    )
    return response.name


def reset_chat():
    st.session_state['message_history'] = []
    st.session_state['session_thread'] = get_thread_id()


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)


def load_conversation(thread_id):
    return bot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    ).values.get('messages', [])


###################################### session state ###########################################

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


if 'session_thread' not in st.session_state:
    st.session_state['session_thread'] = get_thread_id()


if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = list(
        retrieve_all_threads()
    )


if 'chat_names' not in st.session_state:
    st.session_state['chat_names'] = {}

    # Generate names for old chats
    for thread in st.session_state['chat_threads']:

        messages = load_conversation(thread)

        if messages:

            first_message = next(
                (
                    msg
                    for msg in messages
                    if isinstance(msg, HumanMessage)
                ),
                None
            )

            if first_message:

                st.session_state['chat_names'][thread] = generate_chat_name(
                    first_message.content
                )


add_thread(
    st.session_state['session_thread']
)


######################################## sidebar ##########################################

st.sidebar.title('Lang Graph Chat Bot')


if st.sidebar.button('Start a new Chat'):

    # If current chat is empty, remove it
    if not st.session_state['message_history']:

        if st.session_state['session_thread'] in st.session_state['chat_threads']:

            st.session_state['chat_threads'].remove(
                st.session_state['session_thread']
            )

        st.session_state['chat_names'].pop(
            st.session_state['session_thread'],
            None
        )

    reset_chat()

    add_thread(
        st.session_state['session_thread']
    )


st.sidebar.header('Previous Chats')


for thread in st.session_state['chat_threads'][::-1]:

    chat_name = st.session_state['chat_names'].get(
        thread,
        "New Chat"
    )

    if st.sidebar.button(
        chat_name,
        key=f"chat_{thread}"
    ):

        st.session_state['session_thread'] = thread

        messages = load_conversation(thread)

        temp = []

        for msg in messages:

            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'

            temp.append(
                {
                    'role': role,
                    'content': msg.content
                }
            )

        st.session_state['message_history'] = temp


####################################################################################

for message in st.session_state['message_history']:

    with st.chat_message(message['role']):

        st.text(
            message['content']
        )


user_input = st.chat_input(
    'Enter the text here'
)


if user_input:

    current_thread = st.session_state['session_thread']


    # Generate chat name only for new chat
    if current_thread not in st.session_state['chat_names']:

        chat_name = generate_chat_name(
            user_input
        )

        st.session_state['chat_names'][current_thread] = chat_name


    st.session_state['message_history'].append(
        {
            'role': 'user',
            'content': user_input
        }
    )


    with st.chat_message('user'):

        st.text(
            user_input
        )


    with st.chat_message('assistant'):

        with st.status(
            "Thinking..."
        ) as status:


            def response_generator():

                first_chunk = True

                for message_chunk, metadata in bot.stream(
                    {
                        'messages': [
                            HumanMessage(
                                content=user_input
                            )
                        ]
                    },
                    config={
                        'configurable': {
                            'thread_id': st.session_state['session_thread']
                        }
                    },
                    stream_mode='messages'
                ):

                    if first_chunk:

                        status.update(
                            label="Responding...",
                            state="complete",
                            expanded=True
                        )

                        first_chunk = False


                    yield message_chunk.content


            ai_mmsg = st.write_stream(
                response_generator()
            )


        st.session_state['message_history'].append(
            {
                'role': 'assistant',
                'content': ai_mmsg
            }
        )