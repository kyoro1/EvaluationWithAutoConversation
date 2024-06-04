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
tools.load_prompts(prompt_name='evaluate_prompt',
                    prompt_path='./prompts/evaluation.yml')

## Extract prompt candidates
caller_prompt_list = list(tools.promptBank['caller_prompt']['PROMPTS'].keys())
operator_prompt_list = list(tools.promptBank['operator_prompt']['PROMPTS'].keys())
evaluator_prompt_list = list(tools.promptBank['evaluate_prompt']['PROMPTS'].keys())



## Sidebar
with st.sidebar:
    st.title('Auto-Conversation with AOAI API')

    ## Select prompt for caller and operator
    flag_prompt_caller = st.radio(
        "Prompt for caller",
        caller_prompt_list
    )

    flag_prompt_operator = st.radio(
        "Prompt for operator",
        operator_prompt_list
    )
    
    flag_prompt_evaluator = st.radio(
        "Prompt for evaluator",
        evaluator_prompt_list
    )

    ## Set the number of interactions
    conversation_number = st.select_slider("how many interactions?", options=range(1, 10), value=2)

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
    Conversation = tools.generate_conversation(prompt_caller=prompt_caller,
                                                prompt_operator=prompt_operator,
                                                conversation_number=conversation_number,
                                                ui_flg=True)


with st.expander("See explanation"):
    st.write('Evaluation result')
    evaluate_result = tools.evaluate_conversation(prompt_evaluator = tools.promptBank['evaluate_prompt']['PROMPTS']['EVALUATION01'],
                                                    conversation=Conversation)

    # convert json to dataframe
    df = tools.convert_to_df(evaluate_result)
    st.dataframe(df)