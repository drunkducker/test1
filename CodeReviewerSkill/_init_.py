from mycroft import MycroftSkill, intent_file_handler
import pygments
import pydoc
import subprocess
import cursed
import os
import sqlite3

class CodeReviewer(MycroftSkill):
    def __init__(self):
        super().__init__()
        self.add_dirs('locale')
        self.locale_data = self.load_data('locale.json')
        self.conn = sqlite3.connect('code_repository.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS code_snippets (name text, code text)''')
    
    def speak_text(self, key, default_text):
        text = self.translate(key, default_text)
        self.speak(text)

    @intent_file_handler('code.review.intent')
    def handle_code_review(self, message):
        # Extract the code from the user's message
        code = message.data['code']

        # Highlight the code using pygments
        highlighted_code = pygments.highlight(code, pygments.lexers.PythonLexer(), pygments.formatters.TerminalFormatter())

        # Display the highlighted code in the terminal
        self.speak_dialog('code.review.displaying')
        cursed.show(highlighted_code)

    @intent_file_handler('code.explain.intent')
    def handle_code_explain(self, message):
        # Extract the code from the user's message
        code = message.data['code']

        # Generate documentation for the code using pydoc
        documentation = pydoc.getdoc(code)

        # Speak the documentation to the user
        self.speak(documentation)

    @intent_file_handler('code.run.intent')
    def handle_code_run(self, message):
        # Extract the code from the user's message
        code = message.data['code']

        # Save the code to a temporary file
        with open('temp.py', 'w') as f:
            f.write(code)

        # Run the code using subprocess
        try:
            output = subprocess.run(['python', 'temp.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
        # The code snippet is invalid Python code
            self.speak_text('code.run.error', "There was an error running the code. Please make sure the code is valid Python.")
            return

        # Display the output in the terminal
        cursed.show(output.stdout)

        # Remove the temporary file
        os.remove('temp.py')

    @intent_file_handler('code.save.intent')
    def handle_code_save(self, message):
        # Extract the code and the name of the code snippet from the user's message
        code = message.data['code']
        name = message.data['name']

        # Save the code snippet to the code repository
        self.cursor.execute('''INSERT INTO code_snippets VALUES (?, ?)''', (name, code))
        self.conn.commit()

        self.speak_dialog('code.save.success')

    @intent_file_handler('code.retrieve.intent')
    def handle_code_retrieve(self, message):
        # Extract the name of the code snippet from the user's message
        name = message.data['name']

        # Retrieve the code snippet from the code repository
        self.cursor.execute('''SELECT code FROM code_snippets WHERE name=?''', (name,))
        code = self.cursor.fetchone()[0]

    @intent_handler('code.display.directory.chart.intent')
    def handle_display_directory_chart(self, message):
        # List the contents of the current directory
        contents = os.listdir('.')

        # Display the directory chart to the user
        self.speak('The current directory contains the following items:')
        for item in contents:
            self.speak(item)

    @intent_handler('code.open.file.intent')
    def handle_open_file(self, message):
        # Extract the file path from the user's message
        file_path = message.data['path']

        # Open the specified file
        self.open_file(file_path)
    @intent_handler('code.save.intent')
    def handle_save_code(self, message):
        # Extract the name of the code snippet from the user's message
        name = message.data['name']

        # Prompt the user to specify the code they want to save
        self.speak('What code do you want to save?')

        # Wait for the user to respond
        code = self.get_response()

        # Save the code to the code repository
        self.save_code(name, code)



def create_skill():
    return CodeReviewer()