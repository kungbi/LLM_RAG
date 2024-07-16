from openai import OpenAI


class ChatAPI:
    def __init__(self, url, model):
        self.client = OpenAI(base_url=url, api_key="lm-studio")
        self.model = model
        self.history = []

    def send_request_history(self, message):
        self.history.append({"role": "user", "content": message})

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
        )

        new_message = {"role": "assistant", "content": ""}
        new_message["content"] += completion.choices[0].message.content
        self.history.append(new_message)
        return new_message["content"]

    def send_request_history_stream(self, message):
        self.history.append({"role": "user", "content": message})

        completion = self.client.chat.completions.create(
            model=self.model, messages=self.history, stream=True
        )

        self.history.append({"role": "assistant", "content": ""})
        for chunk in completion:
            if chunk.choices[0].delta.content:
                self.history[-1]["content"] += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content

    def send_request(self, message):
        request = [{"role": "user", "content": message}]

        completion = self.client.chat.completions.create(
            model=self.model, messages=request
        )
        return completion.choices[0].message.content


# client = ChatAPI(
#     url="http://localhost:1234/v1",
#     model="lmstudio-community/Meta-Llama-3-8B-Instruct-BPE-fix-GGUF",
# )
# print(client.send_request("hi"))
# print(client.send_request_history("hi"))
# for chunk in client.send_request_history_stream("hi"):
#     print(chunk, end="")
