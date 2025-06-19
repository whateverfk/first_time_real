import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import time

load_dotenv()

class Agent:
    def __init__(self,model = "deepseek/deepseek-r1-0528:free"):
        self.model = model
        self.client = self.set_up_client()

    def set_up_client(self):
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
               "api key bi lor roi"
            )
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key= api_key
            
        )
        
        return client
        
    def call_model(self ,messagesss):

        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messagesss
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM: {e}")
            # Maybe we should retry here?
            return None
        
    def analyze_task(self, user_query):
        system_prompt = """
        You are an AI task planner. Your job is to break down a user's request 
        into a series of clear, discrete steps that can be executed sequentially.

        Respond with a JSON array of steps, where each step has:
        1. A "description" field describing what needs to be done
        2. A "reasoning" field explaining why this step is necessary

        Format your response as a valid JSON array without any additional text.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Break down this task into steps: {user_query}"}
        ]

        response = self.call_model(messages)

        try:
            # Extract the JSON array from the response
            
            print("Error: Could not parse response as JSON")
            print(f"Raw response: {response}")
            steps = json.loads(response)
            return steps
        except json.JSONDecodeError:
            print("Error: Could not parse response as JSON")
            print(f"Raw response: {response}")
            return []
        
    def execute_step(self, step, context):
        """
        Execute a single step in the plan

        Args:
            step (dict): The step to execute
            context (str): Context from previous steps

        Returns:
            str: Result of executing the step
        """
        system_prompt = """
        You are an AI assistant focusing on executing a specific task step.
        Use the provided context and step description to complete this specific step only.
        Your response should be detailed and directly address the step's requirements.
        """

        step_msg = f"Context so far: {context}\n\nExecute this step: {step['description']}\n\nReasoning: {step['reasoning']}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": step_msg}
        ]

        return self.call_model(messages)

    def compile_results(self, steps_results, user_query):
        """
        Compile the results of all steps into a final response

        Args:
            steps_results (list): Results from each executed step
            user_query (str): The original user query

        Returns:
            str: Final compiled response
        """
        system_prompt = """
        You are an AI assistant that compiles information from multiple processing steps 
        into a coherent, unified response. Your goal is to present the information clearly 
        and directly address the user's original query.
        """

        # Join step results - could probably be a one-liner but this is clearer
        step_texts = []
        for i, res in enumerate(steps_results):
            step_num = i + 1
            step_texts.append(f"Step {step_num} result: {res}")
        steps_text = "\n\n".join(step_texts)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original query: {user_query}\n\nResults from steps:\n{steps_text}\n\nPlease provide a comprehensive, unified response to the original query."}
        ]

        return self.call_model(messages)

    def solve(self, user_query):
        """
        Solve a task through multi-step reasoning

        Args:
            user_query (str): The user's request

        Returns:
            dict: A dictionary containing the original query, steps taken, 
                  results of each step, and the final response
        """
        print(f"🤔 Analyzing task: {user_query}")
        steps = self.analyze_task(user_query)

        if not steps:
            return {"error": "Could not break down the task into steps"}

        print(f"📋 Breaking down into {len(steps)} steps:")
        for i, step in enumerate(steps):
            print(f"  {i+1}. {step['description']}")

        step_results = []  # Going with snake_case here, inconsistent with camelCase elsewhere
        context = ""

        for i, step in enumerate(steps):
            print(f"\n⚙️ Executing step {i+1}: {step['description']}")
            result = self.execute_step(step, context)
            step_results.append(result)
            context += f"\nStep {i+1} result: {result}"
            print(f"  ✅ Completed")
            # Add a small delay to avoid rate limits
            time.sleep(1)  # Maybe this should be configurable?

        print("\n🔄 Compiling final response...")
        final_response = self.compile_results(step_results, user_query)

        return {
            "query": user_query,
            "steps": steps,
            "step_results": step_results,  # Note: variable name changed from steps_results
            "final_response": final_response
        }

def main():
    """Main function to demonstrate the agent's capabilities"""
    # Initialize the agent with a capable model
    agent = Agent(model="nvidia/llama-3.3-nemotron-super-49b-v1:free")

    # Example query - we used to have a different one about travel planning
    user_query = "Research and suggest three possible vacation destinations for a family with young children, considering budget-friendly options."

    # Solve the task
    result = agent.solve(user_query)

    # Print the final response
    print("\n" + "=" * 50)
    print("FINAL RESPONSE:")
    print("=" * 50)
    print(result["final_response"])    


if __name__ == "__main__":
    main()

        