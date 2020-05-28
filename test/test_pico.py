import unittest
from server import _get_pico_for_tiab

class PICOSpanTest(unittest.TestCase):

    def test_empty(self):
        results = _get_pico_for_tiab([''], [''])

        self.assertEqual(len(results), 1)
        result = results[0]

        self.assertEqual(len(result['population']), 0)
        self.assertEqual(len(result['interventions']), 0)
        self.assertEqual(len(result['outcomes']), 0)

    def test_single(self):
        title = """
            The AtRial Cardiopathy and Antithrombotic Drugs In prevention After cryptogenic stroke randomized trial: Rationale and methods.
        """
        abstract = """
            Recent data suggest that a thrombogenic atrial substrate can cause stroke in the absence of atrial fibrillation. Such an atrial cardiopathy may explain some proportion of cryptogenic strokes. The aim of the ARCADIA trial is to test the hypothesis that apixaban is superior to aspirin for the prevention of recurrent stroke in subjects with cryptogenic ischemic stroke and atrial cardiopathy. 1100 participants. Biomarker-driven, randomized, double-blind, active-control, phase 3 clinical trial conducted at 120 U.S. centers participating in NIH StrokeNet. Patients ≥ 45 years of age with embolic stroke of undetermined source and evidence of atrial cardiopathy, defined as ≥ 1 of the following markers: P-wave terminal force >5000 µV × ms in ECG lead V1, serum NT-proBNP > 250 pg/mL, and left atrial diameter index ≥ 3 cm/m2 on echocardiogram. Exclusion criteria include any atrial fibrillation, a definite indication or contraindication to antiplatelet or anticoagulant therapy, or a clinically significant bleeding diathesis. Intervention: Apixaban 5 mg twice daily versus aspirin 81 mg once daily. Analysis: Survival analysis and the log-rank test will be used to compare treatment groups according to the intention-to-treat principle, including participants who require open-label anticoagulation for newly detected atrial fibrillation. The primary efficacy outcome is recurrent stroke of any type. The primary safety outcomes are symptomatic intracranial hemorrhage and major hemorrhage other than intracranial hemorrhage. ARCADIA is the first trial to test whether anticoagulant therapy reduces stroke recurrence in patients with atrial cardiopathy but no known atrial fibrillation.
        """
        results = _get_pico_for_tiab([title], [abstract])

        self.assertEqual(len(results), 1)
        result = results[0]

        self.assertEqual(len(result['population']), 6)
        self.assertIn('1100 participants', result['population'])
        self.assertIn('patients with atrial cardiopathy but no known atrial fibrillation', result['population'])
        self.assertEqual(len(result['interventions']), 5)
        self.assertIn('apixaban', result['interventions'])
        self.assertIn('aspirin', result['interventions'])
        self.assertEqual(len(result['outcomes']), 3)
        self.assertIn('stroke recurrence', result['outcomes'])
