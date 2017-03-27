import surveymonty
import json
import pandas as pd

ACCESS_TOKEN = 'EnNFL-zHZRlZsfo-ucA6k0Z3VL3bWXx2MzNoRn.rV44HLh2nP5ZByx9xx8bOKGCvlgRQsjvpEIkEB.FbmAX7fW2crAdJeWbgbsOJlX147aBgYB.3JVR7d4NEvTrhj42kPAtijHFK3GmkcXxr0q-S.aDFNNNibxBL2pfO0lC1OW8='
API_KEY = 'jmgru2v76xmzhauxzvtgj7d2'

api = surveymonty.Client(ACCESS_TOKEN, API_KEY)

surveys = api.get_survey_list()
surveys = surveys['surveys']

cahps_surveys = []
question_map = pd.DataFrame()
for survey in surveys:
    survey_detail = api.get_survey_details(survey['survey_id'])
    if "2016 Patient Experience of Care Survey" in survey_detail['title']['text']:
        cahps_surveys.append(survey_detail['survey_id'])
        questions = {}
        for page in survey_detail['pages']:
            for question in page['questions']:
                questions[question['question_id']] = [question['heading']]
                questions[question['question_id']].append(question['position'])
                for answer in question['answers']:
                    questions[question['question_id']].append(answer['text'])
                    if 'position' in answer:
                        questions[question['question_id']].append(answer['position'])
                    else:
                        questions[question['question_id']].append(' ')
                    questions[question['question_id']].append(answer['answer_id'])
        x = pd.DataFrame.from_dict(questions, orient='index').sort_values(by=0)
        x.to_csv(survey['survey_id'] + '_questions.csv')
        question_map[survey['survey_id']] = x.index.tolist()
question_map.to_csv('question_map.csv')


##for survey in cahps_surveys:
##    respondent_ids = []
##    respondents = api.get_respondent_list(survey)
##    for respondent in respondents['respondents']:
##        respondent_ids.append(respondent['respondent_id'])
##    responses = api.get_all_responses(survey, respondent_ids)
##    with open(survey + '_responses.txt', 'w') as outfile:
##        json.dump(responses, outfile)
    
    
##for page in survey_detail['pages']:
##	for x in page:
##		print(x)
