brochure_user_prompt: str = """You are looking at a company called: {company_name}. Analyze the contents of its website and create a concise, 
professional brochure about the company. Use only the information gathered from the company website Do Not create missing information just skip that section. omit the header and any description text if information is missing

use icons within the brochure

"Please create a one-page markdown brochure for the {company_name} page

"""

# Example only be creative in your design each time
#
# 1. **Title**: A compelling headline that encapsulates the page's mission.
#
# 2. **Introduction**: A brief overview emphasizing the page's main topic.
#
# 3. **Featured Topics**: Organize recent page posts into relevant categories. For each post, provide:
#    - **Title**: The title of the page post.
#    - **Date**: The publication date. only if available. If not do not include date header section
#    - **Summary**: A concise description of the page's content.
#    # - **Link**: A 'Read more →' hyperlink directing to the full post.
#
# 4. **Why Follow {company_name}?**: Highlight the page's strengths, such as trusted expertise, a holistic focus, and its commitment to empowering readers.
#
# 5. **Call to Action**: Encourage readers to explore all resources by visiting the {company_name} page and provide links to social media platforms for staying connected.
#
# 6. **Footer**: Conclude with an empowering statement reinforcing the page's mission.
#
# Ensure the brochure is well-structured, visually appealing, and uses consistent formatting. Incorporate emojis and bold headers to enhance readability and engagement."
#
# This prompt guides the creation of a structured and engaging markdown brochure that effectively showcases the {company_name} page's offerings.