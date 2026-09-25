1. **Separate the navigation layer from the logic layer**
   - Navigation: URLs, file paths, download protocols
   - Logic: dependencies, motifs, ciphers

2. **Make the symbolic IDs canonical**
   - Every document gets a stable symbolic ID
   - Every reference uses that ID
   - URLs become metadata, not primary keys

3. **Make the ciphers first-class**
   - Every document has a cipher
   - The cipher is the compressed essence
   - The cipher can be used to reconstruct the document

4. **Make the dependency graph explicit**
   - Not just "extends" but "depends on"
   - Not just "related to" but "derives from"
   - Show the **evolutionary** order

5. **Make it navigable by AI**
   - The XREF should be the **entry point** for any AI working on the corpus
   - It should tell the AI what exists, what it depends on, and how to align