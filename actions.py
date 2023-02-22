from playsound import playsound

def play(path, n: int=1):
    """Play sound file n times."""
    for i in range(n):
        playsound(path)
