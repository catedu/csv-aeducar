def save_results(data):
    with open("results.txt", "a") as f:
        f.write(data + "\n")
