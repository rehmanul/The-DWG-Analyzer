
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.webview import WebView
import threading
import subprocess
import time

class ArchitecturalAnalyzerApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='AI Architectural Space Analyzer PRO',
            size_hint_y=None,
            height=50,
            font_size=20
        )
        layout.add_widget(title)
        
        # Start button
        start_btn = Button(
            text='Launch Analyzer',
            size_hint_y=None,
            height=50,
            on_press=self.start_streamlit
        )
        layout.add_widget(start_btn)
        
        # WebView for Streamlit
        self.webview = WebView(url='http://localhost:8501')
        layout.add_widget(self.webview)
        
        return layout
    
    def start_streamlit(self, instance):
        """Start Streamlit in background thread"""
        def run_streamlit():
            subprocess.run([
                'python', '-m', 'streamlit', 'run', 'streamlit_app.py',
                '--server.port=8501',
                '--server.headless=true'
            ])
        
        thread = threading.Thread(target=run_streamlit)
        thread.daemon = True
        thread.start()
        
        # Wait and reload webview
        time.sleep(3)
        self.webview.url = 'http://localhost:8501'

if __name__ == '__main__':
    ArchitecturalAnalyzerApp().run()
