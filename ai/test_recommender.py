from model_core import recommend


def main():
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

    result = recommend(liked_texts, disliked_texts, candidate_news)

    print("=== Recommendation Results ===")
    for item in result.items:
        print(f"- {item.title}  (score={item.score:.4f})")


if __name__ == "__main__":
    main()
