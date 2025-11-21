"""Test/Demo script for Policy RAG system."""

from src.rag.retrieval.policy_qa import get_policy_qa


def main():
    """Run demo queries against policy documents."""

    print("=" * 60)
    print("🚀 Travel Policy RAG System Demo")
    print("=" * 60)

    qa_system = get_policy_qa()

    # Example questions
    questions = [
        "What is the daily allowance for E7 grade employees in Tier I cities?",
        "What are the eligibility criteria for air travel?",
        "How much advance can an employee get for travel?",
        "What is local conveyance entitlement?",
        "What expenses are non-reimbursable?",
    ]

    for question in questions:
        print(f"\n{'=' * 60}")
        result = qa_system.query(question)

        print(f"\n❓ Q: {result['question']}")
        print(f"\n✅ A: {result['answer']}")

        if result["sources"]:
            print("\n📚 Sources:")
            for source in result["sources"]:
                print(f"  • {source['metadata']} (Score: {source['score']:.2%})")


if __name__ == "__main__":
    main()
