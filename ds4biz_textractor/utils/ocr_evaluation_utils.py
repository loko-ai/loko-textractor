from pprint import pprint

import Levenshtein
import nltk
import numpy as np
import xlsxwriter
from aiostream import stream
#
# from ds4biz_textractor.business.converters import CONV_FACTORY
# from ds4biz_textractor.utils.format_utils import get_format

# nltk.download("punkt")
ANNOTATION_FOLDER = "ocr_folder"  # le folder possono essere le stesse o diverse
PDF_FOLDER = "ocr_folder"
TEXTRAXT_DOCKER_URL = "http://localhost:8080/ds4biz/textract/0.2/extract"
README_TEXT1 = "Le metriche riportate in questo report fanno riferimento alla distanza di Levenshtein, o distanza di edit. Questa misura calcola il minimo numero di caratteri da cambiare (inserimento, cancellazione o modifica) affinchè le stringhe esaminate diventino uguali. Quando invece si fa riferimento al \"Ratio\", ci riferiamo ad una misura calcolata a partire dalla distanza di Levenshtein e che indica la similarità tra le due stringhe. Il suo valore sarà compreso tra 0 e 1."
README_TEXT2 = "Abbiamo poi utilizzato due diversi approcci per calcolare queste metriche, quello di confrontare l'intero testo e quello di confrontare il testo calcolando le distanze token per token. Nel primo caso si guarderò il testo nel suo insieme, e quindi eventuali piccoli errori dell'OCR peseranno meno, ma nel caso di presenza ampia di rumore la misura ne risentirà. Nel secondo caso, andando a confrontare i token in base alla posizione nel testo, si avrà una misura molto penalizzata da un'eventuale assenza di dettagli, come ad esempio la punteggiaturà."


def create_report_more_documents(results_text, results_tokens, output, general_results=None):

    header_dict = {
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#fff9ae',
        'border': 0}
    metric_dict = {
        'bold': False,
        'text_wrap': True,
        'valign': 'center',
        'align': 'left',
        'fg_color': '#eeeeee',
        'border': 0
    }
    column_name_dict = {
        'bold': True,
        'text_wrap': True,
        'valign': 'center',
        'align': 'left',
        'fg_color': '#fffbcc',
        'border': 0
    }
    group_name_dict = {
        'bold': True,
        'text_wrap': True,
        'valign': 'center',
        'align': 'left',
        'fg_color': '#fff200',
        'border': 0
    }
    output_file_name = "OCR_evaluation"
    workbook = xlsxwriter.Workbook(output)
    header_format = workbook.add_format(header_dict)
    metric_format = workbook.add_format(metric_dict)
    column_name_format = workbook.add_format(column_name_dict)
    group_format = workbook.add_format(group_name_dict)
    worksheet = workbook.add_worksheet("SingleDocumentsPerformances")
    worksheet.merge_range(('A1:F3'), 'Single Documents Metrics', header_format)
    worksheet.write(3, 0, "ID File", column_name_format)
    worksheet.write(3, 1, "File Format", column_name_format)
    worksheet.write(3, 2, "Levenshtein Distance", column_name_format)
    worksheet.write(3, 3, "Levenshtein Ratio", column_name_format)
    worksheet.write(3, 4, "Levenshtein Distance Tokens Mean", column_name_format)
    worksheet.write(3, 5, "Levenshtein Ratio Tokens Mean", column_name_format)
    worksheet.set_column(0, 10, 28)
    worksheet.set_default_row(30)
    row = 4
    col = 0
    for k in results_text.keys():
        worksheet.write(row, col, k, metric_format)
        worksheet.write(row, col + 1, results_text[k]["formato"], metric_format)  # -----------------
        worksheet.write(row, col + 2, results_text[k]["distance"], metric_format)
        worksheet.write(row, col + 3, results_text[k]["similarity_ratio"], metric_format)
        worksheet.write(row, col + 4, results_tokens[k]["distance"]["Mean"], metric_format)
        worksheet.write(row, col + 5, results_tokens[k]["similarity_ratio"]["Mean"], metric_format)
        row += 1
    if general_results != None:
        worksheet2 = workbook.add_worksheet("GeneralPerformances")
        worksheet2.set_column(0, 10, 28)
        worksheet2.set_default_row(30)
        worksheet2.merge_range(('A1:B3'), 'General Documents Performances', header_format)
        worksheet2.merge_range(('A4:B4'), 'Text Analysis', group_format)
        worksheet2.merge_range(('A11:B11'), 'Token Analysis', group_format)
        worksheet2.write(4, 0, "Mean Distance", column_name_format)
        worksheet2.write(5, 0, "Min Distance Reached", column_name_format)
        worksheet2.write(6, 0, "Max Distance Reached", column_name_format)
        worksheet2.write(7, 0, "Mean Ratio", column_name_format)
        worksheet2.write(8, 0, "Min Ratio Reached", column_name_format)
        worksheet2.write(9, 0, "Max Ratio Reached", column_name_format)

        worksheet2.write(4, 1, general_results["text"]["distance"]["mean"], metric_format)
        worksheet2.write(5, 1, general_results["text"]["distance"]["min"], metric_format)
        worksheet2.write(6, 1, general_results["text"]["distance"]["max"], metric_format)
        worksheet2.write(7, 1, general_results["text"]["ratio"]["mean"], metric_format)
        worksheet2.write(8, 1, general_results["text"]["ratio"]["mean"], metric_format)
        worksheet2.write(9, 1, general_results["text"]["ratio"]["mean"], metric_format)

        worksheet2.write(11, 0, "Mean Distance", column_name_format)
        worksheet2.write(12, 0, "Min Distance Reached", column_name_format)
        worksheet2.write(13, 0, "Max Distance Reached", column_name_format)
        worksheet2.write(14, 0, "Mean Ratio", column_name_format)
        worksheet2.write(15, 0, "Min Ratio Reached", column_name_format)
        worksheet2.write(16, 0, "Max Ratio Reached", column_name_format)

        worksheet2.write(11, 1, general_results["tokens"]["distance"]["mean"], metric_format)
        worksheet2.write(12, 1, general_results["tokens"]["distance"]["min"], metric_format)
        worksheet2.write(13, 1, general_results["tokens"]["distance"]["max"], metric_format)
        worksheet2.write(14, 1, general_results["tokens"]["ratio"]["mean"], metric_format)
        worksheet2.write(15, 1, general_results["tokens"]["ratio"]["min"], metric_format)
        worksheet2.write(16, 1, general_results["tokens"]["ratio"]["max"], metric_format)
    worksheet3 = workbook.add_worksheet("READ-ME")
    readme_dict = {
        'font_color': '#000000',
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#ffffff',
        'left': 1,
        'right': 1,
        'top': 1,
        "font_size": 20}
    readme_text1_dict = {
        'bold': False,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': '#ffffff',
        'text_wrap': True,
        'left': 1,
        'right': 1,}
    readme_text2_dict = {
        'bold': False,
        'align': 'left',
        'valign': 'top',
        'fg_color': "#ffffff",
        'left': 1,
        'right': 1,
        'bottom': 1,
        'text_wrap': True,}#'#add58a', "#00a65d"
    readme_format = workbook.add_format(readme_dict)
    readme_text1_format = workbook.add_format(readme_text1_dict)
    readme_text2_format = workbook.add_format(readme_text2_dict)

    worksheet3.merge_range(('A1:G9'), '------------- READ ME -------------', readme_format)
    worksheet3.merge_range(('A10:G20'), README_TEXT1, readme_text1_format)
    worksheet3.merge_range(('A21:G27'), README_TEXT1, readme_text2_format)

    workbook.close()


def compute_tokens_distance(string1, string2):
    distance = Levenshtein.distance(string1, string2)
    return (distance)


def compare_text_tokens(ocr_tokens, annot_tokens, id_file):
    ratio_list = []
    distance_list = []
    for s1, s2 in zip(ocr_tokens, annot_tokens):
        distance = compute_tokens_distance(s1, s2)
        distance_list.append(distance)
        ratio_list.append(((len(s1) + len(s2)) - distance) / (len(s1) + len(s2)))
    results = {id_file: {"distance": {"Total": np.sum(distance_list),
                                      "Mean": np.mean(distance_list),
                                      },
                         "similarity_ratio": {"Total": np.sum(ratio_list),
                                              "Mean": np.mean(ratio_list)
                                              }
                         }
               }
    return results


def get_tokens(text):
    tokens = nltk.word_tokenize(text, language = "italian")
    return tokens


def get_tokens_modified(text):
    tokens = nltk.word_tokenize(text)
    index_to_drop = []
    for i in range(len(tokens)):
        if tokens[i] == "`":
            tokens[i] = tokens[i - 1] + tokens[i]
            index_to_drop += [i - 1]
        elif tokens[i] == "’":
            tokens[i] = tokens[i - 1] + tokens[i] + tokens[i + 1]
            index_to_drop += [i - 1, i + 1]
    new_tokens = np.delete(tokens, index_to_drop)
    return new_tokens

def compute_statistics(measure_list):
    mean_measure = float(np.mean(measure_list))
    min_measure = float(np.min(measure_list))
    max_measure = float(np.max(measure_list))
    return dict(mean = mean_measure, min = min_measure, max =  max_measure)

def compute_general_performance_results(results, token_results):
    ratio_list_text = [results[k]["similarity_ratio"] for k in results.keys()]
    distance_list_text = [results[k]["distance"] for k in results.keys()]
    ratio_list_token = [token_results[k]["similarity_ratio"]["Mean"] for k in token_results.keys()]
    distance_list_token = [token_results[k]["distance"]["Total"] for k in token_results.keys()]
    general_results = {"text": {"ratio": compute_statistics(ratio_list_text),
                                "distance": compute_statistics(distance_list_text)},
                       "tokens": {"ratio": compute_statistics(ratio_list_token),
                                  "distance": compute_statistics(distance_list_token)}}
    return general_results


def document_performance_computation(s1, s2, id_file):
    distance = compute_tokens_distance(s1, s2)
    ratio = ((len(s1) + len(s2)) - distance) / (len(s1) + len(s2))
    results_text = {id_file: {"distance": distance,
                              "similarity_ratio": ratio}
                    }
    ocr_tokens = get_tokens_modified(s1)
    annot_tokens = get_tokens_modified(s2)
    results_tokens = compare_text_tokens(ocr_tokens, annot_tokens, id_file)
    return (results_text, results_tokens)



async def documents_performance(files, annotated, report=False, output = ''):
    zipped_files = stream.zip(files, annotated)  # TODO controllare funzioni nel caso di documenti singoli e zippati

    results_text = {}
    results_tokens = {}

    async for file, annot in zipped_files:
        s1 = file['text']
        s2 = annot['text']
        id_file = annot["filename"].replace('.txt', '')
        partial_results_text, partial_results_tokens = document_performance_computation(s1, s2, id_file)

        results_text.update(partial_results_text)
        results_text[id_file]["formato"] =  file["filename"].split(".")[-1].lower()
        results_tokens.update(partial_results_tokens)

    general_results = compute_general_performance_results(results_text, results_tokens)

    if report:
        create_report_more_documents(results_text, results_tokens, output, general_results)

    return general_results


if __name__ == '__main__':
    with open('../test/test_resources/docswithannotations/01.doc', 'rb') as f:
        f1 = f
    with open('../test/test_resources/docswithannotations/01.txt', 'rb') as f:
        f2 = f

    res = documents_performance(files = f1, annotated = f2, report=True)
    pprint(res)

    # many_documents_performance(PDF_FOLDER, ANNOTATION_FOLDER, TEXTRAXT_DOCKER_URL)
    # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    # ocr_text = ocr(PDF_FILENAME, TEXTRAXT_DOCKER_URL)
    # print(type(ocr_text["text"]))

    # ocr_tokens = get_tokens_modified(ocr_text["text"])
    # annot_tokens = get_tokens_modified(text_annot)
    # print(ocr_tokenmany_documents_performance(pdf_folder, annot_folder, textract_docker_url)s[:100])
    # text_annot = read_txt(TXT_FILENAME)
    # print(type(text_annot))

    # annot_tokens = get_tokens_modified(text_annot)
    # print(annot_tokens[:100])
    # levenshtein = ocr_evaluation(PDF_FILENAME, TXT_FILENAME, TEXTRAXT_DOCKER_URL)
    # print(levenshtein)
    # save_metrics(TXT_FILENAME, levenshtein)
    # string1 = ocr_text["text"]#[:92]
    # string2 = text_annot#[:92]
    # ratio = fuzz.ratio(string1, string2)
    # print(ratio)
    # distance = compute_tokens_distance(string1, string2)
    # print(distance)
    # ratio2 = ((len(string1) + len(string2)) - distance) / (len(string1) + len(string2))
    # # print(len('bellevento'), len("bell'evento"))
    # print(ratio2)
    # print(len(string1), len(string2))
    # print(len(string1)- len(string2))
    #
    # print(len(ocr_tokens), len(annot_tokens))

    # Levenshtein.d
    # {'Total distance': 10645, 'Minimum token distance': 0, 'Maximum token distance': 15, 'Mean token distance': 5.417302798982188}
    # Togliendo bellevento:
    # {'Total distance': 10258, 'Minimum token distance': 0, 'Maximum token distance': 15, 'Mean token distance': 5.220356234096692}

    # come presentare le metriche e come implementare piu' file
