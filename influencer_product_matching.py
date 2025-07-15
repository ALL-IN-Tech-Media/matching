from typing import List, Dict, Any, Callable
from dataclasses import dataclass, field

# 1. Influencer Data Model (extensible)
@dataclass
class Influencer:
    id: str
    name: str
    attributes: Dict[str, Any]  # e.g. {'followers': 10000, 'exposure': 50000, ...}
    hashtags: List[str] = field(default_factory=list)
    video_tags: List[str] = field(default_factory=list)

    def all_tags(self) -> List[str]:
        """Combine all tags for matching."""
        return list(set(self.hashtags + self.video_tags))

# --- Import video_to_text for video tag extraction ---
from matching.video_to_text import video_to_text
import re

def extract_video_tags(videos: List[str]) -> List[List[str]]:
    """
    Analyze a list of videos and return a list of hashtag lists for each video.
    Args:
        videos (List[str]): List of video file paths or URLs.
    Returns:
        List[List[str]]: List of hashtag lists for each video.
    """
    prompt = (
        "You are a great specialist. You are good at tagging videos. "
        "This is a video, please extract all useful hashtag from the video."
    )
    tag_lists = []
    for video_path in videos:
        text = video_to_text(video_path, prompt=prompt)
        # Extract hashtags from the output text (e.g., #tag1 #tag2 ...)
        tags = re.findall(r"#\w+", text)
        # If no hashtags, try to split by common delimiters (fallback)
        if not tags:
            tags = re.split(r"[,;\s]", text)
            tags = [t.strip("# ") for t in tags if t.strip()]
        tag_lists.append(tags)
    return tag_lists

# 3. Input filtering function (to extract useful content from user input)
def filter_user_input(user_input: str) -> List[str]:
    """Extract keywords or hash tags from user input for matching."""
    # TODO: Implement more advanced filtering if needed
    # For now, split by whitespace and lowercase
    return [w.lower() for w in user_input.strip().split() if w]

# 4. Hash tag matching function
def match_influencers(user_tags: List[str], influencers: List[Influencer]) -> List[Influencer]:
    """Return influencers whose tags overlap with user_tags."""
    matched = []
    for inf in influencers:
        if set(user_tags) & set(inf.all_tags()):
            matched.append(inf)
    return matched

# 5. Flexible sorting function
def sort_influencers(influencers: List[Influencer], sort_key: str, reverse: bool = True) -> List[Influencer]:
    """Sort influencers by a given attribute (e.g., 'followers', 'exposure')."""
    return sorted(
        influencers,
        key=lambda inf: inf.attributes.get(sort_key, 0),
        reverse=reverse
    )

# 6. Add video tags to influencer
def add_video_tags_to_influencer(influencer: Influencer, video_tags: List[str]):
    """
    Add extracted video tags to the influencer's video_tags list (deduplicated).
    """
    influencer.video_tags = list(set(influencer.video_tags).union(set(video_tags)))

# 7. Example usage (mock data)
if __name__ == "__main__":
    # Example influencer database
    influencers = [
        Influencer(
            id="1",
            name="达人A",
            attributes={"followers": 120000, "exposure": 500000, "budget": 10000},
            hashtags=["美妆", "护肤", "口红"],
            video_tags=["彩妆", "新品"]
        ),
        Influencer(
            id="2",
            name="达人B",
            attributes={"followers": 80000, "exposure": 200000, "budget": 5000},
            hashtags=["家电", "厨房"],
            video_tags=["烹饪", "美食"]
        ),
        Influencer(
            id="3",
            name="达人C",
            attributes={"followers": 300000, "exposure": 1000000, "budget": 20000},
            hashtags=["运动", "健身"],
            video_tags=["跑步", "瑜伽"]
        ),
    ]

    # Example: extract video tags for a list of videos and add to influencer
    video_list = ["./videos/tiktok_@.aplacetoheal_0.mp4"]
    tag_lists = extract_video_tags(video_list)
    print("Extracted video tags:", tag_lists)
    # Add tags to the first influencer as a demo
    if tag_lists:
        add_video_tags_to_influencer(influencers[0], tag_lists[0])
        print("Updated influencer video_tags:", influencers[0].video_tags)

    # User search input
    user_input = "美妆 彩妆 预算10000以上"
    user_tags = filter_user_input(user_input)

    # Match influencers
    matched = match_influencers(user_tags, influencers)
    print(f"Matched influencers: {[inf.name for inf in matched]}")

    # Sort by followers
    sorted_by_followers = sort_influencers(matched, sort_key="followers")
    print("Sorted by followers:", [(inf.name, inf.attributes["followers"]) for inf in sorted_by_followers])

    # Sort by budget
    sorted_by_budget = sort_influencers(matched, sort_key="budget")
    print("Sorted by budget:", [(inf.name, inf.attributes["budget"]) for inf in sorted_by_budget]) 