# SimplePythonBrowser

I am writing a python browser using this book written by Pavel Panchekha & Chris Harrelson:

https://browser.engineering/

### Usage

- Currently it is terminal only, but I will make a GUI soon
- Supports both HTTP and HTTPS, as well as custom ports (using HTTP of course)
- I also added crude support for FILE and DATA schemes
- FILE example:  
  `windows: python main.py "file://c:/Test/Test.html"`  
  `linux: python main.py "file:///Home/User/Test.html"`  
- DATA example: `data:text/html,HTML test`

To run it, in the terminal type:
`python main.py YourURL`

