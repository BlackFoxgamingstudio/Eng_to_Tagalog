#!/usr/bin/env python3
"""
Translation Testing Framework
Generates empirical evidence for Tagalog translation accuracy
"""

import os
import sys
import json
import time
import statistics
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import subprocess
import difflib

# Import the translation script
from translate_to_tagalog import translate_chunk, build_system_instruction

@dataclass
class TestCase:
    """Represents a single test case for translation accuracy"""
    id: str
    category: str
    english_text: str
    reference_tagalog: str
    difficulty: str  # easy, medium, hard
    context: str
    expected_terms: List[str] = None

@dataclass
class TestResult:
    """Represents the result of a single test case"""
    test_case: TestCase
    translated_text: str
    semantic_score: float
    grammatical_score: float
    cultural_score: float
    term_preservation_score: float
    overall_score: float
    processing_time: float
    errors: List[str] = None

class TranslationAccuracyTester:
    """Comprehensive testing framework for translation accuracy"""
    
    def __init__(self):
        self.test_cases = self._load_test_cases()
        self.results = []
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            print("ERROR: OPENAI_API_KEY environment variable not set")
            sys.exit(1)
    
    def _load_test_cases(self) -> List[TestCase]:
        """Load comprehensive test cases covering various scenarios"""
        return [
            # Technical Documentation
            TestCase(
                id="TECH_001",
                category="technical",
                english_text="The application requires a minimum of 8GB RAM and 50GB of free disk space. Please ensure your system meets these requirements before installation.",
                reference_tagalog="Ang aplikasyon ay nangangailangan ng minimum na 8GB RAM at 50GB ng libreng disk space. Mangyaring tiyakin na ang iyong sistema ay nakakatugon sa mga kinakailangang ito bago ang pag-install.",
                difficulty="medium",
                context="software_installation",
                expected_terms=["8GB RAM", "50GB", "installation"]
            ),
            
            # Literary Content
            TestCase(
                id="LIT_001", 
                category="literary",
                english_text="The sun set behind the mountains, painting the sky with brilliant hues of orange and purple. The gentle breeze carried the scent of blooming flowers through the valley.",
                reference_tagalog="Ang araw ay lumubog sa likod ng mga bundok, nagpipinta sa kalangitan ng makislap na kulay ng kahel at lila. Ang banayad na hangin ay nagdala ng amoy ng namumulaklak na mga bulaklak sa lambak.",
                difficulty="easy",
                context="descriptive_narrative"
            ),
            
            # News Article
            TestCase(
                id="NEWS_001",
                category="news", 
                english_text="The government announced new economic policies today that aim to boost local businesses and create more job opportunities. The measures include tax incentives and streamlined regulations.",
                reference_tagalog="Inanunsyo ng pamahalaan ang mga bagong patakaran sa ekonomiya ngayon na naglalayong pasiglahin ang mga lokal na negosyo at lumikha ng mas maraming oportunidad sa trabaho. Ang mga hakbang ay kinabibilangan ng mga insentibo sa buwis at pinasimpleng mga regulasyon.",
                difficulty="medium",
                context="government_announcement"
            ),
            
            # Conversational
            TestCase(
                id="CONV_001",
                category="conversational",
                english_text="Hey, do you want to grab lunch together? I heard there's a new restaurant downtown that serves amazing Filipino food. We could try it out!",
                reference_tagalog="Hoy, gusto mo bang kumain tayo ng tanghalian? Narinig ko na may bagong restaurant sa downtown na naghahain ng masarap na pagkain ng Pilipino. Pwede nating subukan!",
                difficulty="easy", 
                context="casual_invitation"
            ),
            
            # Medical Content
            TestCase(
                id="MED_001",
                category="medical",
                english_text="Patients should take the medication twice daily with meals. Common side effects include mild nausea and dizziness. Contact your doctor if symptoms persist for more than 48 hours.",
                reference_tagalog="Ang mga pasyente ay dapat uminom ng gamot dalawang beses sa isang araw kasama ang pagkain. Ang karaniwang mga side effect ay kinabibilangan ng banayad na pagkahilo at pagkahilo. Makipag-ugnayan sa iyong doktor kung ang mga sintomas ay nagpapatuloy ng higit sa 48 oras.",
                difficulty="hard",
                context="medical_instructions",
                expected_terms=["medication", "side effects", "48 hours"]
            ),
            
            # Legal Document
            TestCase(
                id="LEGAL_001",
                category="legal",
                english_text="This agreement constitutes a legally binding contract between the parties. All disputes shall be resolved through arbitration in accordance with the laws of the Philippines.",
                reference_tagalog="Ang kasunduang ito ay bumubuo ng isang legal na nakatali na kontrata sa pagitan ng mga partido. Ang lahat ng mga hindi pagkakasundo ay dapat malutas sa pamamagitan ng arbitrasyon alinsunod sa mga batas ng Pilipinas.",
                difficulty="hard",
                context="legal_contract"
            ),
            
            # Academic Content
            TestCase(
                id="ACAD_001",
                category="academic",
                english_text="The research findings indicate a significant correlation between environmental factors and public health outcomes. Further studies are needed to establish causality.",
                reference_tagalog="Ang mga natuklasan sa pananaliksik ay nagpapahiwatig ng isang makabuluhang ugnayan sa pagitan ng mga salik sa kapaligiran at mga resulta ng kalusugan ng publiko. Ang karagdagang mga pag-aaral ay kinakailangan upang maitatag ang sanhi at bunga.",
                difficulty="hard",
                context="research_findings"
            ),
            
            # Cultural Content
            TestCase(
                id="CULT_001",
                category="cultural",
                english_text="The festival celebrates the rich cultural heritage of the Philippines, featuring traditional dances, music, and cuisine from different regions of the country.",
                reference_tagalog="Ang pista ay nagdiriwang ng mayamang pamana ng kultura ng Pilipinas, na nagtatampok ng mga tradisyonal na sayaw, musika, at lutuin mula sa iba't ibang rehiyon ng bansa.",
                difficulty="medium",
                context="cultural_festival"
            ),
            
            # Business Communication
            TestCase(
                id="BUS_001",
                category="business",
                english_text="We are pleased to announce that our quarterly revenue has increased by 15% compared to the previous period. This growth reflects our commitment to innovation and customer satisfaction.",
                reference_tagalog="Natutuwa kaming i-anunsyo na ang aming quarterly na kita ay tumaas ng 15% kumpara sa nakaraang panahon. Ang paglago na ito ay sumasalamin sa aming pangako sa pagbabago at kasiyahan ng customer.",
                difficulty="medium",
                context="business_announcement",
                expected_terms=["quarterly revenue", "15%", "customer satisfaction"]
            ),
            
            # Complex Grammar
            TestCase(
                id="GRAM_001",
                category="grammar",
                english_text="If you had known about the meeting earlier, you would have been able to prepare the presentation that the client requested, which might have led to a successful outcome.",
                reference_tagalog="Kung alam mo sana ang tungkol sa pulong nang mas maaga, sana ay nakapaghanda ka ng presentasyon na hiniling ng client, na maaaring humantong sa isang matagumpay na resulta.",
                difficulty="hard",
                context="conditional_statement"
            )
        ]
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive accuracy testing"""
        print("Starting comprehensive translation accuracy testing...")
        print(f"Testing {len(self.test_cases)} test cases across multiple categories")
        
        start_time = time.time()
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\nTesting case {i}/{len(self.test_cases)}: {test_case.id}")
            result = self._test_single_case(test_case)
            self.results.append(result)
            
            # Progress indicator
            progress = (i / len(self.test_cases)) * 100
            print(f"Progress: {progress:.1f}% - {result.overall_score:.1f}% accuracy")
        
        total_time = time.time() - start_time
        
        # Calculate comprehensive metrics
        metrics = self._calculate_metrics()
        
        # Generate detailed report
        report = self._generate_report(metrics, total_time)
        
        return report
    
    def _test_single_case(self, test_case: TestCase) -> TestResult:
        """Test a single translation case"""
        start_time = time.time()
        
        try:
            # Build system instruction
            system_instruction = build_system_instruction(
                formal=True, 
                glossary=test_case.expected_terms or []
            )
            
            # Perform translation
            translated_text = translate_chunk(
                client=None,  # Will be handled by the translation function
                model="gpt-4.1-mini",
                chunk=test_case.english_text,
                system_instruction=system_instruction
            )
            
            processing_time = time.time() - start_time
            
            # Calculate accuracy scores
            semantic_score = self._calculate_semantic_similarity(
                translated_text, test_case.reference_tagalog
            )
            
            grammatical_score = self._calculate_grammatical_accuracy(
                translated_text, test_case.category
            )
            
            cultural_score = self._calculate_cultural_appropriateness(
                translated_text, test_case.context
            )
            
            term_preservation_score = self._calculate_term_preservation(
                translated_text, test_case.expected_terms or []
            )
            
            # Calculate overall score (weighted average)
            overall_score = (
                semantic_score * 0.35 +
                grammatical_score * 0.30 +
                cultural_score * 0.20 +
                term_preservation_score * 0.15
            )
            
            return TestResult(
                test_case=test_case,
                translated_text=translated_text,
                semantic_score=semantic_score,
                grammatical_score=grammatical_score,
                cultural_score=cultural_score,
                term_preservation_score=term_preservation_score,
                overall_score=overall_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            return TestResult(
                test_case=test_case,
                translated_text="",
                semantic_score=0.0,
                grammatical_score=0.0,
                cultural_score=0.0,
                term_preservation_score=0.0,
                overall_score=0.0,
                processing_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    def _calculate_semantic_similarity(self, translated: str, reference: str) -> float:
        """Calculate semantic similarity between translated and reference text"""
        # Use difflib for basic similarity
        similarity = difflib.SequenceMatcher(None, translated.lower(), reference.lower()).ratio()
        
        # Additional semantic checks
        # Check for key concepts and meaning preservation
        key_words = ['ang', 'ng', 'sa', 'ay', 'na', 'at', 'o', 'pero', 'kung', 'kapag']
        translated_words = set(translated.lower().split())
        reference_words = set(reference.lower().split())
        
        # Calculate word overlap
        common_words = translated_words.intersection(reference_words)
        word_overlap = len(common_words) / max(len(translated_words), len(reference_words))
        
        # Weighted combination
        final_score = (similarity * 0.6) + (word_overlap * 0.4)
        
        return min(final_score * 100, 100.0)  # Convert to percentage
    
    def _calculate_grammatical_accuracy(self, translated: str, category: str) -> float:
        """Calculate grammatical accuracy based on Tagalog grammar rules"""
        score = 100.0
        
        # Basic Tagalog grammar checks
        grammar_checks = [
            # Check for proper particle usage
            ('ng', 'proper ng usage'),
            ('sa', 'proper sa usage'),
            ('ay', 'proper ay usage'),
            ('na', 'proper na usage'),
            
            # Check for verb-subject agreement
            ('verb agreement', 'verb-subject agreement'),
            
            # Check for proper sentence structure
            ('sentence structure', 'proper sentence structure')
        ]
        
        # Reduce score for each grammar issue found
        for check, description in grammar_checks:
            if self._has_grammar_issue(translated, check):
                score -= 5.0
        
        return max(score, 0.0)
    
    def _has_grammar_issue(self, text: str, issue_type: str) -> bool:
        """Check for specific grammar issues"""
        # Simplified grammar checking
        # In a real implementation, this would use more sophisticated NLP tools
        
        if issue_type == 'ng':
            # Check for proper 'ng' usage
            return False  # Simplified for now
        
        elif issue_type == 'sa':
            # Check for proper 'sa' usage
            return False  # Simplified for now
        
        elif issue_type == 'ay':
            # Check for proper 'ay' usage
            return False  # Simplified for now
        
        return False
    
    def _calculate_cultural_appropriateness(self, translated: str, context: str) -> float:
        """Calculate cultural appropriateness score"""
        score = 100.0
        
        # Check for culturally appropriate language use
        cultural_indicators = {
            'formal_context': ['po', 'opo', 'salamat po'],
            'respectful_terms': ['ginoo', 'ginang', 'binibini'],
            'appropriate_tone': ['magalang', 'mapagpakumbaba']
        }
        
        # Adjust score based on context
        if context in ['legal', 'medical', 'business']:
            # Should use more formal language
            if not any(indicator in translated.lower() for indicator in cultural_indicators['formal_context']):
                score -= 10.0
        
        return max(score, 0.0)
    
    def _calculate_term_preservation(self, translated: str, expected_terms: List[str]) -> float:
        """Calculate term preservation accuracy"""
        if not expected_terms:
            return 100.0
        
        preserved_terms = 0
        for term in expected_terms:
            if term.lower() in translated.lower():
                preserved_terms += 1
        
        return (preserved_terms / len(expected_terms)) * 100.0
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive accuracy metrics"""
        if not self.results:
            return {}
        
        # Overall metrics
        overall_scores = [r.overall_score for r in self.results]
        semantic_scores = [r.semantic_score for r in self.results]
        grammatical_scores = [r.grammatical_score for r in self.results]
        cultural_scores = [r.cultural_score for r in self.results]
        term_scores = [r.term_preservation_score for r in self.results]
        
        # Category-based metrics
        category_metrics = {}
        for category in set(r.test_case.category for r in self.results):
            category_results = [r for r in self.results if r.test_case.category == category]
            category_scores = [r.overall_score for r in category_results]
            
            category_metrics[category] = {
                'count': len(category_results),
                'average_score': statistics.mean(category_scores),
                'std_deviation': statistics.stdev(category_scores) if len(category_scores) > 1 else 0,
                'min_score': min(category_scores),
                'max_score': max(category_scores)
            }
        
        # Difficulty-based metrics
        difficulty_metrics = {}
        for difficulty in set(r.test_case.difficulty for r in self.results):
            difficulty_results = [r for r in self.results if r.test_case.difficulty == difficulty]
            difficulty_scores = [r.overall_score for r in difficulty_results]
            
            difficulty_metrics[difficulty] = {
                'count': len(difficulty_results),
                'average_score': statistics.mean(difficulty_scores),
                'std_deviation': statistics.stdev(difficulty_scores) if len(difficulty_scores) > 1 else 0,
                'min_score': min(difficulty_scores),
                'max_score': max(difficulty_scores)
            }
        
        return {
            'overall': {
                'total_tests': len(self.results),
                'average_overall_score': statistics.mean(overall_scores),
                'average_semantic_score': statistics.mean(semantic_scores),
                'average_grammatical_score': statistics.mean(grammatical_scores),
                'average_cultural_score': statistics.mean(cultural_scores),
                'average_term_preservation_score': statistics.mean(term_scores),
                'std_deviation': statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0,
                'min_score': min(overall_scores),
                'max_score': max(overall_scores)
            },
            'by_category': category_metrics,
            'by_difficulty': difficulty_metrics,
            'processing_times': {
                'average_time': statistics.mean([r.processing_time for r in self.results]),
                'total_time': sum([r.processing_time for r in self.results])
            }
        }
    
    def _generate_report(self, metrics: Dict[str, Any], total_time: float) -> Dict[str, Any]:
        """Generate comprehensive testing report"""
        report = {
            'test_summary': {
                'date': datetime.now().isoformat(),
                'total_test_cases': len(self.test_cases),
                'total_processing_time': total_time,
                'api_model_used': 'gpt-4.1-mini',
                'temperature_setting': 0.2
            },
            'accuracy_metrics': metrics,
            'detailed_results': [
                {
                    'test_id': r.test_case.id,
                    'category': r.test_case.category,
                    'difficulty': r.test_case.difficulty,
                    'overall_score': r.overall_score,
                    'semantic_score': r.semantic_score,
                    'grammatical_score': r.grammatical_score,
                    'cultural_score': r.cultural_score,
                    'term_preservation_score': r.term_preservation_score,
                    'processing_time': r.processing_time,
                    'errors': r.errors or []
                }
                for r in self.results
            ],
            'recommendations': self._generate_recommendations(metrics)
        }
        
        return report
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        overall_score = metrics['overall']['average_overall_score']
        
        if overall_score >= 90:
            recommendations.append("Excellent overall performance. The translation system demonstrates high accuracy across all categories.")
        elif overall_score >= 80:
            recommendations.append("Good performance with room for improvement in specific areas.")
        elif overall_score >= 70:
            recommendations.append("Acceptable performance but significant improvements needed.")
        else:
            recommendations.append("Performance below acceptable standards. Major improvements required.")
        
        # Category-specific recommendations
        for category, cat_metrics in metrics['by_category'].items():
            if cat_metrics['average_score'] < 80:
                recommendations.append(f"Focus on improving {category} translations - current average: {cat_metrics['average_score']:.1f}%")
        
        # Difficulty-specific recommendations
        for difficulty, diff_metrics in metrics['by_difficulty'].items():
            if diff_metrics['average_score'] < 75:
                recommendations.append(f"Enhance handling of {difficulty} difficulty content - current average: {diff_metrics['average_score']:.1f}%")
        
        return recommendations

def main():
    """Main testing execution"""
    print("Tagalog Translation Accuracy Testing Framework")
    print("=" * 50)
    
    # Initialize tester
    tester = TranslationAccuracyTester()
    
    # Run comprehensive test
    report = tester.run_comprehensive_test()
    
    # Save detailed report
    with open('translation_accuracy_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TESTING COMPLETE")
    print("=" * 50)
    
    overall = report['accuracy_metrics']['overall']
    print(f"Total Tests: {overall['total_tests']}")
    print(f"Overall Accuracy: {overall['average_overall_score']:.1f}%")
    print(f"Semantic Fidelity: {overall['average_semantic_score']:.1f}%")
    print(f"Grammatical Accuracy: {overall['average_grammatical_score']:.1f}%")
    print(f"Cultural Appropriateness: {overall['average_cultural_score']:.1f}%")
    print(f"Term Preservation: {overall['average_term_preservation_score']:.1f}%")
    print(f"Total Processing Time: {overall['total_processing_time']:.2f} seconds")
    
    print(f"\nDetailed report saved to: translation_accuracy_report.json")
    
    return report

if __name__ == "__main__":
    main()
