# 🚀 IntraLingo - HuggingFace Spaces Deployment Guide

## Prerequisites

✅ HuggingFace account (free): https://huggingface.co/join  
✅ Git installed on your computer  
✅ Your fine-tuned model downloaded from Colab  

---

## 📁 Project Structure for Deployment

```
IntraLingo/
├── app.py                    # Rename app_hf.py to app.py
├── requirements.txt          # Rename requirements_hf.txt
├── README.md                 # Project documentation
├── .gitignore               # Git ignore file
├── src/
│   ├── __init__.py
│   ├── parser/
│   │   ├── __init__.py
│   │   └── document_parser.py
│   └── translation/
│       ├── __init__.py
│       └── translator.py
└── models/
    └── nllb-finetuned/      # Your fine-tuned model
        ├── config.json
        ├── generation_config.json
        ├── model.safetensors
        ├── sentencepiece.bpe.model
        ├── special_tokens_map.json
        ├── tokenizer_config.json
        └── tokenizer.json
```

---

## 🎯 Step-by-Step Deployment

### Step 1: Prepare Your Local Repository

1. **Organize files:**
   ```bash
   cd IntraLingo
   
   # Rename files for deployment
   cp app_hf.py app.py
   cp requirements_hf.txt requirements.txt
   
   # Ensure model is in place
   # models/nllb-finetuned/ should contain your fine-tuned model files
   ```

2. **Verify structure:**
   ```bash
   ls -R
   # Should show all folders: src/, models/, etc.
   ```

### Step 2: Create HuggingFace Space

1. **Go to HuggingFace:** https://huggingface.co/spaces

2. **Click "Create new Space"**

3. **Configure Space:**
   - **Owner:** Your username
   - **Space name:** `intralingo` (or your preferred name)
   - **License:** `mit` (or your choice)
   - **Space SDK:** Select **Streamlit**
   - **Visibility:** Public (or Private if you prefer)
   - **Space hardware:** CPU (free) - model will still work, just slower

4. **Click "Create Space"**

### Step 3: Upload Your Code

**Option A: Using Git (Recommended)**

```bash
# Initialize git if not already done
cd IntraLingo
git init

# Add HuggingFace remote
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/intralingo

# Add all files
git add .

# Commit
git commit -m "Initial deployment of IntraLingo"

# Push to HuggingFace
git push space main
```

**Option B: Using Web Interface**

1. In your Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. Drag and drop all your files and folders
4. Commit the changes

### Step 4: Handle Large Model Files

⚠️ **Important:** Git has file size limits (~5GB total, 50MB per file)

Your `model.safetensors` is ~2.5GB, which is fine, but needs Git LFS (Large File Storage):

```bash
# Install Git LFS (one time)
git lfs install

# Track large model files
git lfs track "models/nllb-finetuned/*.safetensors"
git lfs track "models/nllb-finetuned/*.bin"

# Add .gitattributes
git add .gitattributes

# Now add and commit as normal
git add models/
git commit -m "Add fine-tuned model"
git push space main
```

**Alternative:** If model is too large, you can:
1. Upload model to HuggingFace Model Hub separately
2. Modify `translator.py` to download from there
3. (More complex, but works for very large models)

### Step 5: Wait for Build

1. Go to your Space page: `https://huggingface.co/spaces/YOUR_USERNAME/intralingo`
2. You'll see "Building..." status
3. First build takes 5-10 minutes (installing dependencies)
4. Watch the logs for any errors

### Step 6: Test Your Deployment

1. Once build completes, you'll see "Running" status
2. Click **"App"** tab to see your deployed app
3. Upload a test document
4. Verify translation works
5. Check that format is preserved

---

## 🔧 Troubleshooting Common Issues

### Build Fails: "Package not found"

**Fix:** Check `requirements.txt` versions are compatible
```
# Use more flexible versions
transformers>=4.35.0
torch>=2.0.0
streamlit>=1.30.0
```

### "Out of Memory" Error

**Fix:** Upgrade to better hardware in Space settings
- Settings → Hardware → Select "CPU Upgrade" or "GPU"
- Free tier: CPU basic (works but slow)
- Paid: $0.30/hour for GPU T4 (much faster)

### Model Not Loading

**Fix:** Check paths in `translator.py`
```python
# Should be:
finetuned_path = 'models/nllb-finetuned'
```

### App Crashes on Large Files

**Fix:** Add file size limit in `app.py`
```python
# In file uploader
uploaded_file = st.file_uploader(
    "Choose a .docx file",
    type=['docx'],
    help="Max file size: 10MB"
)

if uploaded_file and uploaded_file.size > 10 * 1024 * 1024:  # 10MB
    st.error("File too large! Please upload files under 10MB.")
    return
```

---

## 🎨 Customization After Deployment

### Update README with Your Info

Edit `README.md`:
- Add your contact information
- Update "Contact" section
- Add screenshots
- Include usage examples

### Add Custom Domain (Optional)

HuggingFace Spaces supports custom domains:
1. Go to Space Settings
2. Add your domain
3. Configure DNS

### Monitor Usage

- Check Space "Analytics" tab for visitor stats
- Review logs for errors
- Gather user feedback

---

## 💰 Cost Considerations

### Free Tier (CPU Basic):
- ✅ No cost
- ✅ Unlimited users
- ⚠️ Slower translation (~30-60 seconds per doc)
- ⚠️ May sleep after inactivity

### Paid Tier (GPU):
- 💵 ~$0.30/hour for T4 GPU
- ✅ Fast translation (~5-10 seconds per doc)
- ✅ Always running
- ✅ Better user experience

**Recommendation for demo:** Start with free CPU, upgrade to GPU if you get traction.

---

## 🔒 Private vs Public Spaces

**Public (Recommended for demo):**
- ✅ Anyone can access
- ✅ Good for portfolio/demonstration
- ✅ Shows up in search

**Private:**
- ✅ Only you can access (or invited users)
- ✅ Good for client testing before launch
- 💵 Requires Pro subscription ($9/month)

---

## 📊 Post-Deployment Checklist

After successful deployment:

- [ ] Test with multiple document types
- [ ] Verify all formatting preserved
- [ ] Check translation quality on various texts
- [ ] Test both EN→PL and PL→EN
- [ ] Share link with trusted users for feedback
- [ ] Monitor for errors in logs
- [ ] Update README with any findings
- [ ] Consider adding usage analytics

---

## 🎯 Next Steps

1. **Gather feedback:** Share with select users
2. **Iterate:** Fix issues, improve UI
3. **Promote:** Add to portfolio, LinkedIn, etc.
4. **Scale:** Upgrade hardware if needed
5. **Monetize:** Offer custom versions to clients

---

## 🆘 Get Help

**HuggingFace Community:**
- Forum: https://discuss.huggingface.co/
- Discord: https://discord.gg/hugging-face

**Common Resources:**
- Streamlit docs: https://docs.streamlit.io/
- HF Spaces docs: https://huggingface.co/docs/hub/spaces

---

## 🎉 You're Ready!

Follow these steps and you'll have IntraLingo live on HuggingFace Spaces!

**Good luck with your deployment!** 🚀
