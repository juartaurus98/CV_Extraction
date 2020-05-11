import os
import json
from Extraction.Edu import edu_extract_2
from Extraction.Exp import exp_extract
from Extraction.Infor import extract_Infor
from Extraction.Skills import skill_extraction
from pdf_reader.analysis import query_param_follow_keyword

from flair.models import SequenceTagger
from pdf_reader.merge_multiple_pdfs import pdf_reader

model_exp = SequenceTagger.load('Flair_model/ner/ner_exp/best-model.pt')
model_edu = SequenceTagger.load('Flair_model/ner/ner_edu/best-model.pt')

directory = os.fsencode('/home/juartaurus98/Documents/test_12.2/')
data = []
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    filename = os.path.join('/home/juartaurus98/Documents/test_12.2/', filename)
    try:
        file_data = {}
        file_data.update({'Profile': extract_Infor(query_param_follow_keyword('Profile', pdf_reader(filename)[0])[0])})
        file_data.update(
            {'Edu': edu_extract_2(model_edu, query_param_follow_keyword('Edu', pdf_reader(filename)[0])[0])})
        file_data.update({'Exp': exp_extract(model_exp, query_param_follow_keyword('Exp', pdf_reader(filename)[0])[0])})
        file_data.update({'Skill': skill_extraction(query_param_follow_keyword('Skill', pdf_reader(filename)[0])[0])})
        file_data.update({'file_path': filename})
        data.append(file_data)
    except:
        print(filename)
        pass
