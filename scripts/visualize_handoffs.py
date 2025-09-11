import os
import re
import graphviz
import tempfile

HANDOFF_DIR = 'handoffs'

def parse_handoff_section(content, section_title):
    """
    Parses the content of a specific section from a handoff file.
    e.g., section_title = "1. Summary of Work"
    """
    pattern = re.compile(
        r"## \d+\. " + re.escape(section_title) + r"\n(.*?)(?=\n## \d+\. |\Z)",
        re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(content)
    if match:
        text = match.group(1).strip()
        text = re.sub(r'\n\s*\n', '\n', text)
        # Escape characters for DOT's HTML-like labels
        text = text.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<BR/>')
        # Limit length to avoid huge nodes
        return text[:500] + '...' if len(text) > 500 else text
    return "Not found."

def create_handoff_visualization():
    """
    Generates a PNG graph from handoff files and returns the path.
    """
    try:
        filenames = sorted([f for f in os.listdir(HANDOFF_DIR) if f.endswith('.md')])
    except FileNotFoundError:
        print(f"Error: Directory '{HANDOFF_DIR}' not found.")
        return None

    dot = graphviz.Digraph('Handoffs', comment='The Strange Loop Handoff History')
    dot.attr('graph',
             rankdir='TB',
             bgcolor='transparent',
             label='The Strange Loop: Handoff Evolution',
             fontname='Helvetica,Arial,sans-serif',
             fontsize='20',
             fontcolor='#FFFFFF')
    dot.attr('node',
             shape='box',
             style='rounded,filled',
             fillcolor='#2d3748', # gray-800
             fontname='Helvetica,Arial,sans-serif',
             fontsize='10',
             fontcolor='#E2E8F0', # gray-200
             penwidth='1.5',
             color='#4A5568') # gray-600
    dot.attr('edge',
             color='#718096', # gray-500
             arrowhead='vee',
             penwidth='1.0')

    nodes = []
    for filename in filenames:
        node_id = filename.replace('.md', '')
        nodes.append(node_id)
        filepath = os.path.join(HANDOFF_DIR, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        summary = parse_handoff_section(content, "Summary of Work")
        decisions = parse_handoff_section(content, "Key Decisions")
        lessons = parse_handoff_section(content, "Lessons Learned")

        label = f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" COLOR="#4A5568">'
        label += f'<TR><TD ALIGN="LEFT" BGCOLOR="#1A202C"><B>{node_id}</B></TD></TR>'
        label += f'<TR><TD ALIGN="LEFT" BALIGN="LEFT">'
        label += f'<B>Summary:</B><BR/>{summary.replace("- ", "<BR/>- ")}<BR/><BR/>'
        label += f'<B>Decisions:</B><BR/>{decisions.replace("- ", "<BR/>- ")}<BR/><BR/>'
        label += f'<B>Lessons:</B><BR/>{lessons.replace("- ", "<BR/>- ")}'
        label += f'</TD></TR></TABLE>>'

        dot.node(node_id, label=label)

    for i in range(len(nodes) - 1):
        dot.edge(nodes[i], nodes[i+1])

    # Render the graph to a temporary file
    # The format is specified, and a temporary file is created.
    # The cleanup=True argument will remove the source file after rendering.
    output_path = os.path.join('scratch', 'handoff_graph')
    rendered_path = dot.render(output_path, format='png', view=False, cleanup=True)

    return rendered_path

if __name__ == '__main__':
    image_path = create_handoff_visualization()
    if image_path:
        # The script now prints the path to the generated image,
        # which the agent can then use with another tool.
        print(image_path)
