from agents.locator_agent import LocatorAgent

agent = LocatorAgent()
ssm = {
    'screen_name': 'Login',
    'elements': [
        {'label': 'Username', 'type': 'text_field', 'actions': ['tap'], 'confidence': 0.95},
        {'label': 'Password', 'type': 'password_field', 'actions': ['tap'], 'confidence': 0.94},
        {'label': 'LOGIN', 'type': 'button', 'actions': ['tap'], 'confidence': 0.97},
    ],
}
steps = 'Verify Username field is displayed\nEnter Username\nEnter Password\nTap LOGIN button'
print(agent.generate_locators(ssm, steps))
