#!/usr/bin/env python3
"""
Debug script for search functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.dse_api import DSEAPIService

def test_search_step_by_step():
    dse = DSEAPIService()

    print("🔍 Step 1: Getting quotes content...")
    content = dse._make_request(dse.endpoints['quotes_txt'])
    print(f"Content received: {len(content) if content else 0} characters")

    print("\n🔍 Step 2: Parsing quotes...")
    company_list = dse._parse_quotes_txt(content)
    print(f"Companies parsed: {len(company_list)}")

    print("\n🔍 Step 3: Looking for GP...")
    gp_matches = []
    for company in company_list:
        symbol = company.get('symbol', '').lower()
        if 'gp' in symbol:
            gp_matches.append(company)

    print(f"GP matches found: {len(gp_matches)}")
    for match in gp_matches:
        print(f"  {match}")

    print("\n🔍 Step 4: Testing search function...")
    search_results = dse.search_stocks('GP')
    print(f"Search function results: {len(search_results)}")
    for result in search_results:
        print(f"  {result}")

    print("\n🔍 Step 5: Testing search with different queries...")
    test_queries = ['gp', 'GP', 'Gp', 'BRAC', 'brac', 'uni']
    for query in test_queries:
        results = dse.search_stocks(query)
        print(f"Query '{query}': {len(results)} results")

if __name__ == "__main__":
    test_search_step_by_step()