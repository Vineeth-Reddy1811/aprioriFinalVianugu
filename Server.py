from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from itertools import combinations
from markupsafe import escape


app = Flask(__name__)
app = Flask(__name__, template_folder='./templates')            #indicating where the website files are located

app.config["UPLOAD_FOLDER"] = "temporaryfiles/"         #Storing path to save the uploaded file


@app.route('/')             #Default app def that is executed when the localhost link is provided
def Selecting_file():
    return render_template('index.html')            #Loading index.html file


@app.route('/Output', methods=['GET', 'POST'])                 #Def that is executed to get second page
def Data_handling():
    if request.method == 'POST':
        f = request.files['file']                               #Taking in file to upload
        filename = secure_filename(f.filename)
        f.save(app.config['UPLOAD_FOLDER'] + filename)           #Saving file in the "Temporary files" folder
        f = open(app.config['UPLOAD_FOLDER'] + filename, 'r')
        transactions = []
        for line in f.readlines():                              #Handling data in the given CSV file
            cells = line.split(',')
            element_cells = cells[1:]
            element_cells = [int(cell.strip()) for cell in element_cells]
            transactions.append(element_cells)

        min_sup = int(request.form["min_sup"])                  #taking in min_sup value and storing in min_sup

        output = apriori(transactions, min_sup)                 #Storing the generated itemsets(output) in "output" variable
        return render_template('Output.html', output=output, total_items=len(output))
    return render_template('index.html')


def generate_frequent_items(D, C_k, min_sup):
    element_count = {}
    for transaction in D:              # Scanning D for Counts
        for item in C_k:
            if item.issubset(transaction):      #get the subset of t that are candidates
                if item in element_count:
                    element_count[item] += 1
                else:
                    element_count[item] = 1

    transactions_count = len(D)
    frequent_items = []                         #finding the frequent items which have higher min_sup
    for item in element_count:
        support = element_count[item]
        if support >= min_sup:
            frequent_items.append(item)

    return frequent_items



#use prior knowledge to return all the elements in frequent_items.
def has_infrequent_subset(candidate, frequent_items):
    return candidate in frequent_items


def apriori_gen(frequent_items, k):
    C_k = []
    for l1, l2 in combinations(frequent_items, 2):
        Union = l1 & l2
        if len(Union) == k:
            c = l1 | l2
            if has_infrequent_subset(c, C_k):           #Purne step: remove unfruitful candidates
                C_k.remove(c)
            else:
                C_k.append(c)                           #join step: generate candidates
    return C_k


def find_frequent_1_itemset(D, min_sup):              #finding the first level of frequent items.
    C_1 = []
    for transaction in D:
        for item in transaction:
            item = frozenset([item])
            if item not in C_1:
                C_1.append(item)
    L_1 = generate_frequent_items(D, C_1, min_sup)
    return L_1

def apriori(D, min_sup):
    L = [set(find_frequent_1_itemset(D, min_sup))]                #find all the level 1 frequent item sets satistying minsup
    k = 1
    while len(L[k - 1]) > 0:
        C_k = apriori_gen(L[k - 1], k - 1)
        L.append(set(generate_frequent_items(D, C_k, min_sup)))
        k += 1
    return [set(s) for s in set.union(L[0], *L[1:])]


if __name__ == '__main__':
    app.run(debug=True)


