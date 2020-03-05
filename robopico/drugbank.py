#
#   drugbank.ca lookup
#

"""
substitutes mentions of drugs in a string with the generic name
"""

import data as rpd
import pickle as pickle
import re


class Drugbank:
    def __init__(self):
        with open(rpd.get_data('drugbank/drugbank.pck'), 'rb') as f:
            self.data = pickle.load(f)
            self.description = pickle.load(f)

    def sub(self, text):
        tokens = re.split("([^A-Za-z0-9])", text)
        drug_entities = self._find_longest_token_matches(tokens)

        output = []
        last_marker = 0

        for drug_entity in drug_entities:
            output.extend(tokens[last_marker:drug_entity[1]])
            output.append(drug_entity[0])
            last_marker = drug_entity[2]+1

        output.extend(tokens[last_marker:])
        return ''.join(output)

    def contains_drug(self, text):
        tokens = re.split("([^A-Za-z0-9])", text)
        drug_entities = self._find_longest_token_matches(tokens)

        return len(drug_entities) > 0

    def _find_longest_token_matches(self, tokens):
        output = []
        last_tokens_buffer = [[]]
        # the list contains an empty list which acts as a dummy placeholder
        # since the loop below iterates through the outer list, adding the
        # current word to each sublist

        temp_buffer = [[]]
        # this is a copy, since a completely new buffer is developed with
        # each iteration of the loop
        
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            token_tags = []

            for token_list in last_tokens_buffer:
                
                lookup_key = "".join(token_list + [token_lower])
                # make a copy to stop the pop deleting items from the gazetteer below!
                result = self.data.get(lookup_key, set()).copy()

                while result:
                    item = result.pop()
                    if item == "!!jump!!":
                        temp_buffer.append(token_list + [token_lower])
                    else:
                        token_tags.append((item, i-len(token_list), i))

            last_tokens_buffer = temp_buffer
            temp_buffer = [[]]

            if token_tags:
                output.extend(token_tags)

        return output


def main():
    drugbank = Drugbank()

    test_text = """
    Here is some text which mentions tylenol, ibuprofen, quinine, and valproic acid.
    """

    print(test_text)
    print()
    print(drugbank.sub(test_text))
    print(drugbank.contains_drug(test_text))

    
    test_text = """
    Here is some more text which contains no drug mention.
    """

    print(test_text)
    print()
    print(drugbank.sub(test_text))
    print(drugbank.contains_drug(test_text))


if __name__ == '__main__':
    main()
