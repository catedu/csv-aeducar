def save_results(data):
    with open("data/results.txt", "a") as f:
        f.write(data + "\n")
