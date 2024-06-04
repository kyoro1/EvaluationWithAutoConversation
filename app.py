import streamlit as st
from src import common

## Initialization of the tools
tools = common.AOAI_TOOLS(config_file='./config.yml')
## Load configuration
tools.load_config()

## Load operational prompts
tools.load_prompts(prompt_name='caller_prompt',
					prompt_path='./prompts/caller_prompts.yml')
tools.load_prompts(prompt_name='operator_prompt',
					prompt_path='./prompts/operator_prompts.yml')

## Extract prompt candidates
caller_prompt_list = list(tools.promptBank['caller_prompt']['PROMPTS'].keys())
operator_prompt_list = list(tools.promptBank['operator_prompt']['PROMPTS'].keys())

st.title('Auto-Conversation with AOAI API')

## Sidebar
with st.sidebar:
    ## Select prompt for caller and operator
    flag_prompt_caller = st.radio(
        "Prompt for caller",
        caller_prompt_list
    )

    flag_prompt_operator = st.radio(
        "Prompt for operator",
        operator_prompt_list
    )

    ## Set the number of interactions
    conversation_number = st.select_slider("how many interactions?", options=range(1, 10), value=3)

    with st.form("my_form"):
        st.write("Ready to start?")
        # Every form must have a submit button.
        submitted = st.form_submit_button("Start conversation")
        if submitted:
            st.write(f'Start auto-conversation with {conversation_number} interaction(s).')

if not submitted:
    st.stop()
else:
    ## Set configuration for AOAI client
    tools.setClient()

    ## Define initial prompt for caller
    prompt_caller = tools.promptBank['caller_prompt']['PROMPTS'][flag_prompt_caller]
    ## Define initial prompt for operator
    prompt_operator = tools.promptBank['operator_prompt']['PROMPTS'][flag_prompt_operator]

    ## Generate conversation
    tools.generate_conversation_on_UI(prompt_caller=prompt_caller,
                                      prompt_operator=prompt_operator,
                                      conversation_number=conversation_number)