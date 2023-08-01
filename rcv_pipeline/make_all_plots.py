import os

def main():
    models = os.listdir('../output')
    for model in models:
        if model != '.DS_Store':
            print(f'Plotting {model}')
            os.system(f'python plots_no_ac.py {model}')

if __name__=="__main__":
    main()