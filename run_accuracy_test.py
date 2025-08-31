#!/usr/bin/env python3
"""
Simplified Translation Accuracy Test Runner
Provides real empirical evidence for translation accuracy
"""

import os
import sys
import json
import time
from datetime import datetime
from openai import OpenAI

# Test cases with reference translations
TEST_CASES = [
    {
        "id": "TECH_001",
        "category": "technical",
        "english": "The application requires a minimum of 8GB RAM and 50GB of free disk space.",
        "reference": "Ang aplikasyon ay nangangailangan ng minimum na 8GB RAM at 50GB ng libreng disk space.",
        "expected_terms": ["8GB RAM", "50GB"]
    },
    {
        "id": "LIT_001",
        "category": "literary", 
        "english": "The sun set behind the mountains, painting the sky with brilliant hues of orange and purple.",
        "reference": "Ang araw ay lumubog sa likod ng mga bundok, nagpipinta sa kalangitan ng makislap na kulay ng kahel at lila.",
        "expected_terms": []
    },
    {
        "id": "NEWS_001",
        "category": "news",
        "english": "The government announced new economic policies today that aim to boost local businesses.",
        "reference": "Inanunsyo ng pamahalaan ang mga bagong patakaran sa ekonomiya ngayon na naglalayong pasiglahin ang mga lokal na negosyo.",
        "expected_terms": []
    },
    {
        "id": "CONV_001", 
        "category": "conversational",
        "english": "Hey, do you want to grab lunch together? I heard there's a new restaurant downtown.",
        "reference": "Hoy, gusto mo bang kumain tayo ng tanghalian? Narinig ko na may bagong restaurant sa downtown.",
        "expected_terms": []
    },
    {
        "id": "MED_001",
        "category": "medical",
        "english": "Patients should take the medication twice daily with meals. Contact your doctor if symptoms persist.",
        "reference": "Ang mga pasyente ay dapat uminom ng gamot dalawang beses sa isang araw kasama ang pagkain. Makipag-ugnayan sa iyong doktor kung ang mga sintomas ay nagpapatuloy.",
        "expected_terms": ["medication", "symptoms"]
    }
]

def calculate_similarity(text1, text2):
    """Calculate basic text similarity"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) * 100

def check_term_preservation(translated_text, expected_terms):
    """Check if expected terms are preserved"""
    if not expected_terms:
        return 100.0
    
    preserved = 0
    for term in expected_terms:
        if term.lower() in translated_text.lower():
            preserved += 1
    
    return (preserved / len(expected_terms)) * 100

def check_grammar_indicators(translated_text):
    """Check for basic Tagalog grammar indicators"""
    score = 100.0
    
    # Check for basic Tagalog particles
    particles = ['ang', 'ng', 'sa', 'ay', 'na', 'at', 'o']
    found_particles = sum(1 for particle in particles if particle in translated_text.lower())
    
    # Basic grammar score based on particle usage
    if found_particles >= 3:
        score = 95.0
    elif found_particles >= 2:
        score = 85.0
    elif found_particles >= 1:
        score = 75.0
    else:
        score = 60.0
    
    return score

def run_accuracy_test():
    """Run the actual accuracy test"""
    print("Tagalog Translation Accuracy Test")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your API key: export OPENAI_API_KEY='your-key-here'")
        return None
    
    # Initialize OpenAI client
    client = OpenAI()
    
    results = []
    total_start_time = time.time()
    
    print(f"Testing {len(TEST_CASES)} cases...")
    print()
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}: {test_case['id']} ({test_case['category']})")
        
        start_time = time.time()
        
        try:
            # Create system instruction
            system_instruction = f"""Ikaw ay isang propesyonal na tagasalin sa Tagalog (Filipino).
Layunin: tumpak at natural na pagsasalin sa Tagalog.
Mga panuntunan:
- Gamitin ang natural at malinaw na Tagalog
- Panatilihin ang mga pangalan, numero, at teknikal na termino
- Iwasan ang literal na salin; gumamit ng katumbas na idyoma
- Huwag magdagdag o magbawas ng impormasyon
- Output: Isang kumpletong salin sa Tagalog"""

            # Perform translation
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Isalin ang sumusunod sa Tagalog: {test_case['english']}"}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            translated_text = response.choices[0].message.content.strip()
            processing_time = time.time() - start_time
            
            # Calculate accuracy metrics
            semantic_score = calculate_similarity(translated_text, test_case['reference'])
            term_preservation = check_term_preservation(translated_text, test_case['expected_terms'])
            grammar_score = check_grammar_indicators(translated_text)
            
            # Overall score (weighted average)
            overall_score = (semantic_score * 0.4 + term_preservation * 0.3 + grammar_score * 0.3)
            
            result = {
                'test_id': test_case['id'],
                'category': test_case['category'],
                'english': test_case['english'],
                'reference': test_case['reference'],
                'translated': translated_text,
                'semantic_score': round(semantic_score, 1),
                'term_preservation': round(term_preservation, 1),
                'grammar_score': round(grammar_score, 1),
                'overall_score': round(overall_score, 1),
                'processing_time': round(processing_time, 2),
                'errors': []
            }
            
            results.append(result)
            
            print(f"  Semantic: {semantic_score:.1f}% | Terms: {term_preservation:.1f}% | Grammar: {grammar_score:.1f}%")
            print(f"  Overall: {overall_score:.1f}% | Time: {processing_time:.2f}s")
            print()
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            result = {
                'test_id': test_case['id'],
                'category': test_case['category'],
                'english': test_case['english'],
                'reference': test_case['reference'],
                'translated': '',
                'semantic_score': 0.0,
                'term_preservation': 0.0,
                'grammar_score': 0.0,
                'overall_score': 0.0,
                'processing_time': time.time() - start_time,
                'errors': [str(e)]
            }
            results.append(result)
            print()
    
    total_time = time.time() - total_start_time
    
    # Calculate overall metrics
    successful_results = [r for r in results if not r['errors']]
    
    if successful_results:
        avg_semantic = sum(r['semantic_score'] for r in successful_results) / len(successful_results)
        avg_terms = sum(r['term_preservation'] for r in successful_results) / len(successful_results)
        avg_grammar = sum(r['grammar_score'] for r in successful_results) / len(successful_results)
        avg_overall = sum(r['overall_score'] for r in successful_results) / len(successful_results)
        avg_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
    else:
        avg_semantic = avg_terms = avg_grammar = avg_overall = avg_time = 0.0
    
    # Generate report
    report = {
        'test_summary': {
            'date': datetime.now().isoformat(),
            'total_tests': len(TEST_CASES),
            'successful_tests': len(successful_results),
            'failed_tests': len(results) - len(successful_results),
            'total_time': round(total_time, 2),
            'model_used': 'gpt-4o-mini',
            'temperature': 0.2
        },
        'accuracy_metrics': {
            'semantic_fidelity': round(avg_semantic, 1),
            'term_preservation': round(avg_terms, 1),
            'grammatical_accuracy': round(avg_grammar, 1),
            'overall_accuracy': round(avg_overall, 1),
            'average_processing_time': round(avg_time, 2)
        },
        'detailed_results': results,
        'category_breakdown': {}
    }
    
    # Category breakdown
    categories = set(r['category'] for r in successful_results)
    for category in categories:
        category_results = [r for r in successful_results if r['category'] == category]
        category_avg = sum(r['overall_score'] for r in category_results) / len(category_results)
        report['category_breakdown'][category] = {
            'count': len(category_results),
            'average_score': round(category_avg, 1)
        }
    
    # Print summary
    print("=" * 40)
    print("TEST RESULTS SUMMARY")
    print("=" * 40)
    print(f"Total Tests: {len(TEST_CASES)}")
    print(f"Successful: {len(successful_results)}")
    print(f"Failed: {len(results) - len(successful_results)}")
    print(f"Total Time: {total_time:.2f} seconds")
    print()
    print("ACCURACY METRICS:")
    print(f"Semantic Fidelity: {avg_semantic:.1f}%")
    print(f"Term Preservation: {avg_terms:.1f}%")
    print(f"Grammatical Accuracy: {avg_grammar:.1f}%")
    print(f"Overall Accuracy: {avg_overall:.1f}%")
    print(f"Average Processing Time: {avg_time:.2f} seconds")
    print()
    
    if report['category_breakdown']:
        print("CATEGORY BREAKDOWN:")
        for category, data in report['category_breakdown'].items():
            print(f"  {category.title()}: {data['average_score']:.1f}% ({data['count']} tests)")
    
    # Save detailed report
    with open('empirical_accuracy_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: empirical_accuracy_report.json")
    
    return report

if __name__ == "__main__":
    run_accuracy_test()
