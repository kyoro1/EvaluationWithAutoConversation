import os
import json
import pandas as pd
import yaml
import openai
from openai import AzureOpenAI
from streamlit_chat import message

class LOAD_CONFIG():
    def __init__(self,
                 config_file: str) -> None:
        ## Prepare config file
        self.config_file = config_file
        self.load_config()

        ## Configuration for Variables
        self.AOAI_client = None
        self.AZURE_ENDPOINT = self.config['AOAI']['ENDPOINT']
        self.AZURE_OPENAI_KEY = self.config['AOAI']['KEY']
        self.AZURE_OPENAI_VER = self.config['AOAI']['VERSION']

        ## PARAMETERS FOR AOAI MODEL
        self.AOAI_MODEL = self.config['AOAI']['MODEL']
        self.AOAI_TEMPERATURE = self.config['AOAI']['PARAMTERS']['TEMPERATURE']
        self.AOAI_MAX_TOKENS = self.config['AOAI']['PARAMTERS']['MAX_TOKENS']
        self.AOAI_TOP_P = self.config['AOAI']['PARAMTERS']['TOP_P']
        self.AOAI_FREQUENCY_PENALTY = self.config['AOAI']['PARAMTERS']['FREQUENCY_PENALTY']
        self.AOAI_PRESENCE_PENALTY = self.config['AOAI']['PARAMTERS']['PRESENCE_PENALTY']

        ## Configuration for prompts
        self.PATH_CALLER_PROMPT = self.config['PROMPTS']['PROMPT_PATH']['CALLER']
        self.PATH_OPERATOR_PROMPT = self.config['PROMPTS']['PROMPT_PATH']['OPERATOR']
        self.PATH_EVALUATOR_PROMPT = self.config['PROMPTS']['PROMPT_PATH']['EVALUATOR']

    def load_config(self):
        '''
        Load and extract config yml file.
        '''
        try:
            ### The file encoding specification (utf-8) is for running on Windows OS.
            ### If not specified, the following error will occur.
            ### UnicodeDecodeError: 'cp932' codec can't decode byte...
            with open(self.config_file, encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            print(e)
            raise

class AOAI_TOOLS(LOAD_CONFIG):
    def __init__(self,
                 config_file: str) -> None:
        super().__init__(config_file)

        ## variables for prompts
        self.promptBank = dict()

        ## list of prompts
        self.caller_prompt_list = []
        self.operator_prompt_list = []
        self.evaluator_prompt_list = []

    def load_prompts(self,
                     prompt_name: str,
                     prompt_path: str) -> list:
        '''
        Load prepared prompts in yml file
        '''
        try:
            ## Open specified prompts
            ### The file encoding specification (utf-8) is for running on Windows OS.
            ### If not specified, the following error will occur.
            ### UnicodeDecodeError: 'cp932' codec can't decode byte...
            with open(prompt_path, encoding='utf-8') as f:
                d = yaml.safe_load(f)
            ## store prompts
            self.promptBank[prompt_name] = d
        except Exception as e:
            print(e)
            raise

    def prepare_prompts(self):
        '''
        Extract prompts from promptBank
        '''
        try:
            # Load operational prompts
            ## For caller
            self.load_prompts(prompt_name='caller_prompt',
                                prompt_path=self.PATH_CALLER_PROMPT)
            ## For operator
            self.load_prompts(prompt_name='operator_prompt',
                                prompt_path=self.PATH_OPERATOR_PROMPT)
            ## For evaluator
            self.load_prompts(prompt_name='evaluate_prompt',
                                prompt_path=self.PATH_EVALUATOR_PROMPT)
            # Extract prompt candidates
            self.caller_prompt_list = list(self.promptBank['caller_prompt']['PROMPTS'].keys())
            self.operator_prompt_list = list(self.promptBank['operator_prompt']['PROMPTS'].keys())
            self.evaluator_prompt_list = list(self.promptBank['evaluate_prompt']['PROMPTS'].keys())
        except Exception as e:
            print(e)
            raise


    def setClient(self):
        '''
        Configuration for client on Azure OpenAI
        '''
        try:
            ## Configuration for AOAI client
            self.AOAI_client = AzureOpenAI(
                azure_endpoint = self.AZURE_ENDPOINT, 
                api_key=self.AZURE_OPENAI_KEY,  
                api_version=self.AZURE_OPENAI_VER
            )
        except Exception as e:
            print(e)
            raise

    def send_message_to_openai(self,
                               message_text:str) -> str:
        try:
            return self.AOAI_client.chat.completions.create(
                                                    model=self.AOAI_MODEL, 
                                                    messages = message_text,
                                                    temperature=self.AOAI_TEMPERATURE,
                                                    max_tokens=self.AOAI_MAX_TOKENS,
                                                    top_p=self.AOAI_TOP_P,
                                                    frequency_penalty=self.AOAI_FREQUENCY_PENALTY,
                                                    presence_penalty=self.AOAI_PRESENCE_PENALTY,
                                                    stop=None
                                                    )
        except Exception as e:
            print(e)
            raise

    def setAOAIformat(self,
                      message:str,
                      role:str) -> dict:
        '''
        Convert message to dict
        '''
        try:
            tmp_prompt = dict()
            tmp_prompt['role'] = role
            tmp_prompt['content'] = message
            return tmp_prompt
        except Exception as e:
            print(e)
            raise

    def extractOutput(self,
                      output: openai.types.chat.chat_completion.ChatCompletion) -> str:
        ''' 
        extract returned message
        '''
        try:
            return output.choices[0].message.content
        except Exception as e:
            print(e)
            raise

    def generate_conversation(self,
                              conversation_number: int,
                              prompt_caller: str,
                              prompt_operator: str,
                              ui_flg: bool=False,) -> list:
        '''
        Generate conversation with both prompts for caller and operator
        '''
        try:
            prompts_caller, prompts_operator, Conversation = [], [], []
            output_operator = None

            ## Define initial prompt for caller as system message
            content_caller_for_caller = self.setAOAIformat(message=prompt_caller, role='system')
            ## Define initial prompt for operator as system message
            content_operator = self.setAOAIformat(message=prompt_operator, role='system')

            for _ in range(conversation_number):
                # Caller -> Operator
                ## Set a message for caller
                prompts_caller.append(content_caller_for_caller)
                ## Set 
                if output_operator is not None:
                    content_operator = self.setAOAIformat(message=self.extractOutput(output_operator), role='assistant')
                    content_operator_for_caller = self.setAOAIformat(message=self.extractOutput(output_operator), role='user')
                    prompts_caller.append(content_operator_for_caller)
                ## a message from caller to operator
                output_caller = self.send_message_to_openai(message_text=prompts_caller)
                ## Store the conversation
                statement_caller = f'Caller  : {self.extractOutput(output_caller)}'
                Conversation.append(statement_caller)
                if ui_flg:
                    message(self.extractOutput(output_caller), is_user=False)
                else:
                    print(statement_caller)

                # Operator -> Caller
                ## Set message by caller
                content_caller = self.setAOAIformat(message=self.extractOutput(output_caller), role='user')
                content_caller_for_caller = self.setAOAIformat(message=self.extractOutput(output_caller), role='assistant')
                ## Set the message in the prompt
                prompts_operator.append(content_operator)
                prompts_operator.append(content_caller)
                ## a message from operator to caller
                output_operator = self.send_message_to_openai(message_text=prompts_operator)

                statement_operator = f'Operator: {self.extractOutput(output_operator)}'
                Conversation.append(statement_operator)
                if ui_flg:
                    message(self.extractOutput(output_operator), is_user=True)
                else:
                    print(statement_operator)

            return Conversation

        except Exception as e:
            print(e)
            raise

    def evaluate_conversation(self,
                              prompt_evaluator: str,
                              conversation: list) -> str:
        '''
        Evaluate conversation
        '''
        try:
            prompts_evaluator = []
            ## Convert conversation to string
            connected_conversation = '\n'.join(conversation)
            ## Set the conversation to the prompt
            prompt_evaluator_to_be_used = prompt_evaluator.replace('<<actual_conversation>>', connected_conversation)

            ## Define initial prompt for caller as system message
            content_caller_for_evaluator = self.setAOAIformat(message=prompt_evaluator_to_be_used, role='system')
            prompts_evaluator.append(content_caller_for_evaluator)
            ## Evaluate with GPT-4
            output_evaluator = self.send_message_to_openai(message_text=prompts_evaluator)
            return self.extractOutput(output_evaluator)
        except Exception as e:
            print(e)
            raise

    def convert_to_df(self,
                     evaluate_result: list) -> pd.DataFrame:
        '''
        Convert evaluation result to DataFrame
        '''
        try:
            json_data = json.loads(evaluate_result)
            return pd.DataFrame(json_data).T        
        except Exception as e:
            print(e)
            raise