import requests

def send_simple_message():
    return requests.post(
        "https://api.mailgun.net/v3/sandbox9d7c2e70651f4d86a0a1f361c7421006.mailgun.org/messages",
        auth=("api", "key-44712adb6782522d773561096ce04494"),
        data={"from": "Rishabh <mailgun@sandbox9d7c2e70651f4d86a0a1f361c7421006.mailgun.org>",
              "to": "rishu.sanklecha@gmail.com",
              "subject": "Rate Limit Reached!",
              "text": "Rate Limit Reached!"})

if __name__ == '__main__':
    send_simple_message()

