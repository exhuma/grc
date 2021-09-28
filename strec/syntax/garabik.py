class Coloriser:

    def load(self, filename):
        with open(filename) as fptr:
            for line in fptr:
                print(line)
