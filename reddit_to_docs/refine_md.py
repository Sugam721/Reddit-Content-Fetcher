from transformers import T5ForConditionalGeneration, T5Tokenizer

# Model location on D: drive
model_path = r"D:\DATASET\t5_story_editing_final"

# Input files on C: drive
input_md_file = r"C:\Users\Sugam Sharma\Desktop\reddit_to_docs\edited_comments.md"

# Output file on C: drive (you can change the name if you want)
output_md_file = r"C:\Users\Sugam Sharma\Desktop\reddit_to_docs\final_comments.md"

# Load model and tokenizer from model folder
tokenizer = T5Tokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)

def refine_comment(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_length=512,
        num_beams=4,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def read_md_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    # Split comments by empty line
    comments = [c.strip() for c in content.split("\n\n") if c.strip()]
    return comments

def save_md_file(comments, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for comment in comments:
            f.write(comment + "\n\n")

# Read edited comments
edited_comments = read_md_file(input_md_file)

# Refine each comment
final_comments = []
for comment in edited_comments:
    refined_comment = refine_comment(comment)
    final_comments.append(refined_comment)

# Save final refined comments
save_md_file(final_comments, output_md_file)

print(f"Refinement done! Saved in:\n{output_md_file}")
