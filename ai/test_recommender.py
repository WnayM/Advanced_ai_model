from recommender import NewsRecommender

def main() -> None:
    liked_texts = [
        "The new season of Jujutsu Kaisen has officially been announced",
        "A new trailer for the upcoming Demon Slayer arc has been released",
    ]

    disliked_texts = [
        "A new gacha mobile game based on a famous anime franchise has been revealed",
    ]

    candidate_news = [
        "One Piece confirms the release date for the next major arc",
        "The director of Attack on Titan shared details about creating the final episode",
        "A collaboration between a popular anime and a mobile game breaks revenue records",
        "A slice-of-life spin-off of My Hero Academia has been announced",
    ]
    
    recommender = NewsRecommender()

    user_vec = recommender.build_user_vector_from_texts(
        liked_texts=liked_texts,
        disliked_texts=disliked_texts,
    )

    top_indices, scores = recommender.rank_candidates(
        user_vector=user_vec,
        candidate_texts=candidate_news,
        top_k=3, 
    )
    
    print("=== Recommendation Results ===")
    for idx in top_indices:
        print(f"- {candidate_news[idx]}  (score={scores[idx]:.4f})")


if __name__ == "__main__":
    main()