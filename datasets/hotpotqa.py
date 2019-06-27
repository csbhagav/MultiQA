import json
from datasets.multiqa_dataset import MultiQA_DataSet
from overrides import overrides
from allennlp.common.file_utils import cached_path
from common.uuid import gen_uuid
import tqdm


class HotpotQA(MultiQA_DataSet):
    """

    """

    def __init__(self):
        self.DATASET_NAME = 'HotpotQA'

    @overrides
    def build_header(self, contexts, split, preprocessor):
        header = {}

        return header

    @overrides
    def build_contexts(self, split, preprocessor):
        #if split == 'train':
        #    single_file_path = cached_path("http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_train_v1.1.json")
        #elif split == 'dev':
        #    single_file_path = cached_path("http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json")
        single_file_path = "/Users/alontalmor/Documents/dev/datasets/HotpotQA/hotpot_" + split + "_distractor_v1.json"

        with open(single_file_path, 'r') as myfile:
            data = json.load(myfile)

        contexts = []
        for example in tqdm.tqdm(data, total=len(data), ncols=80):

            documents = []
            supporting_context = []
            for doc_ind, para in enumerate(example['context']):

                # calcing the sentence_start_bytes for the supporting facts in hotpotqa
                offset = 0
                sentence_start_bytes = [0]
                for sentence in para[1]:
                    offset += len(sentence) + 1
                    sentence_start_bytes.append(offset)
                sentence_start_bytes = sentence_start_bytes[:-1]

                # choosing only the gold paragraphs
                for supp_fact in example['supporting_facts']:
                    # finding the gold context
                    if para[0] == supp_fact[0] and len(sentence_start_bytes) > supp_fact[1]:
                        supporting_context.append({'doc_ind':doc_ind,
                                                   'part':'text',
                                                   'start_byte': sentence_start_bytes[supp_fact[1]],
                                                   'text':para[1][supp_fact[1]]})

                # joining all sentences into one
                documents.append({'text':' '.join(para[1]) + ' ',
                                 'title': para[0],
                                 'metadata': {"text": {"sentence_start_bytes": sentence_start_bytes}}})

            if example['answer'].lower() == 'yes':
                answers = {'abstractive': {'yesno': 'yes'}}
            elif example['answer'].lower() == 'no':
                answers = {'abstractive': {'yesno': 'no'}}
            else:
                answers = {'extractive': {'single_answer': {'answer': example['answer'],
                                      'aliases': [example['answer']]}}}

            qas = [{"qid": example['_id'],
                    "metadata":{'type':example['type'],'level':example['level']},
                    "supporting_context": supporting_context,
                    "question": example['question'],
                    "answers": answers,
                    }]

            contexts.append({"id": self.DATASET_NAME + '_' + example['_id'],
                             "context": {"documents": documents},
                             "qas": qas})

        # tokenize
        # TODO this is only for debugging :
        contexts = contexts[0:5]
        contexts = preprocessor.tokenize_and_detect_answers(contexts)

        # detect answers

        # save dataset

        return contexts