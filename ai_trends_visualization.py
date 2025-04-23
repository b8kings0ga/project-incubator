import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Define data for AI trends visualization
ai_domains = ['Large Language Models', 'Computer Vision', 'Generative AI', 
              'Reinforcement Learning', 'AI for Science', 'Robotics', 
              'AI Ethics & Safety', 'AI Hardware']

# Impact scores (estimated impact on a scale of 1-10)
impact_scores = [9.5, 8.2, 9.8, 7.5, 8.9, 7.8, 8.5, 8.0]

# Growth rate (estimated annual growth as percentage)
growth_rates = [85, 65, 90, 50, 75, 60, 70, 80]

# Research activity (relative number of papers published)
research_activity = [100, 85, 95, 70, 80, 65, 75, 60]

# Create a custom colormap
colors = ["#4a6fe3", "#8a56e2", "#cf4192", "#e73f84", "#fa5e7e", "#ff7e7e", "#ffa270", "#ffc470"]
n_bins = 100
cmap_name = 'custom_diverging'
cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

# Set up the plots
plt.figure(figsize=(18, 12))

# 1. Impact scores bar chart
plt.subplot(2, 2, 1)
bars = plt.bar(ai_domains, impact_scores, color=colors)
plt.ylim(0, 10)
plt.title('Estimated Impact of AI Domains (1-10 scale)', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.ylabel('Impact Score')
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{height}',
             ha='center', va='bottom', fontsize=9)

# 2. Growth rate horizontal bar chart
plt.subplot(2, 2, 2)
y_pos = np.arange(len(ai_domains))
bars = plt.barh(y_pos, growth_rates, color=colors)
plt.yticks(y_pos, ai_domains)
plt.xlabel('Estimated Annual Growth (%)')
plt.title('Growth Rate by AI Domain', fontsize=14)
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height()/2.,
             f'{width}%',
             ha='left', va='center', fontsize=9)

# 3. Bubble chart of impact vs. growth with research activity as size
plt.subplot(2, 1, 2)
plt.scatter(growth_rates, impact_scores, s=[r*10 for r in research_activity], 
            c=np.arange(len(ai_domains)), cmap=cm, alpha=0.7)

plt.xlabel('Estimated Annual Growth (%)')
plt.ylabel('Impact Score (1-10)')
plt.title('AI Domains: Impact vs Growth vs Research Activity', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)

# Add annotations for each bubble
for i, domain in enumerate(ai_domains):
    plt.annotate(domain, 
                 (growth_rates[i], impact_scores[i]),
                 xytext=(7, 0), 
                 textcoords='offset points',
                 fontsize=9)

# Add a legend for bubble size
sizes = [50, 75, 100]
labels = ['Low', 'Medium', 'High']
for i, size in enumerate(sizes):
    plt.scatter([], [], s=size*10, c='gray', alpha=0.7, 
                label=f'{labels[i]} Research Activity')
plt.legend(loc='upper left')

plt.tight_layout()
plt.savefig('AI_Trends_Visualization.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualization created and saved as AI_Trends_Visualization.png")

# Create a second visualization for AI investment trends
plt.figure(figsize=(15, 10))

# Data for AI investment by sector (in billions USD, estimated)
sectors = ['Healthcare', 'Finance', 'Retail', 'Manufacturing', 'Transportation', 
           'Entertainment', 'Education', 'Agriculture']
investment_2022 = [12.5, 15.8, 9.2, 11.5, 8.3, 7.5, 4.2, 3.1]
investment_2023 = [18.7, 22.4, 14.6, 16.8, 13.2, 12.1, 6.8, 5.5]
investment_2024 = [29.5, 35.2, 21.8, 24.5, 19.7, 17.6, 10.2, 8.9]

# Plot stacked bar chart for investment trends
x = np.arange(len(sectors))
width = 0.25

plt.subplot(2, 1, 1)
plt.bar(x - width, investment_2022, width, label='2022', color='#4a6fe3')
plt.bar(x, investment_2023, width, label='2023', color='#cf4192')
plt.bar(x + width, investment_2024, width, label='2024 (Projected)', color='#ffa270')

plt.xlabel('Industry Sectors')
plt.ylabel('Investment (Billions USD)')
plt.title('AI Investment by Industry Sector', fontsize=14)
plt.xticks(x, sectors, rotation=45, ha='right')
plt.legend()

# Add value labels
for i, v in enumerate(investment_2022):
    plt.text(i - width, v + 0.5, f'${v}B', ha='center', fontsize=8)
for i, v in enumerate(investment_2023):
    plt.text(i, v + 0.5, f'${v}B', ha='center', fontsize=8)
for i, v in enumerate(investment_2024):
    plt.text(i + width, v + 0.5, f'${v}B', ha='center', fontsize=8)

# Pie chart for AI talent distribution
plt.subplot(2, 1, 2)
talent_areas = ['Machine Learning', 'Data Science', 'AI Research', 
                'AI Engineering', 'AI Ethics', 'AI Product Management']
talent_distribution = [35, 25, 15, 18, 3, 4]
explode = (0.1, 0, 0, 0, 0.2, 0.1)  # explode slices for emphasis

plt.pie(talent_distribution, explode=explode, labels=talent_areas, autopct='%1.1f%%',
        shadow=True, startangle=140, colors=plt.cm.Spectral(np.linspace(0, 1, len(talent_areas))))
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
plt.title('Global AI Talent Distribution', fontsize=14)

plt.tight_layout()
plt.savefig('AI_Investment_Talent_Visualization.png', dpi=300, bbox_inches='tight')
plt.close()

print("Investment and talent visualization created and saved as AI_Investment_Talent_Visualization.png")