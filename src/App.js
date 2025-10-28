import './Styles/placeholder.css';
import { useState, useEffect } from 'react';
import {
  collection,
  addDoc,
  updateDoc,
  doc,
  getDocs,
  getDoc,
  serverTimestamp,
  query,
  orderBy
} from 'firebase/firestore';
import { firestore } from './firebase';

function App() {
  // Form state
  const [recipeId, setRecipeId] = useState(null);
  const [name, setName] = useState('');
  const [unit, setUnit] = useState('lb');
  const [description, setDescription] = useState('');
  const [notes, setNotes] = useState('');
  const [ingredients, setIngredients] = useState([
    { name: '', weight: '' }
  ]);
  const [status, setStatus] = useState('');
  const [recipesList, setRecipesList] = useState([]); // for loading/viewing existing recipes

  // Load latest recipes for quick selection
  useEffect(() => {
    const load = async () => {
      try {
        const q = query(collection(firestore, 'recipes'), orderBy('updatedAt', 'desc'));
        const snap = await getDocs(q);
        const list = snap.docs.map(d => ({ id: d.id, ...(d.data() || {}) }));
        setRecipesList(list);
      } catch (e) {
        console.warn('Failed to load recipes list', e);
      }
    };
    load();
  }, []);

  const addIngredientRow = () => setIngredients(prev => [...prev, { name: '', weight: '' }]);
  const updateIngredient = (idx, key, val) => {
    setIngredients(prev => prev.map((ing, i) => i === idx ? { ...ing, [key]: val } : ing));
  };
  const removeEmptyIngredients = (arr) => arr.filter(i => i.name.trim() || i.weight !== '');

  const clearForm = () => {
    setRecipeId(null);
    setName('');
    setUnit('lb');
    setDescription('');
    setNotes('');
    setIngredients([{ name: '', weight: '' }]);
  };

  // Create a new blank recipe document and load it
  const createRecipeFromScratch = async () => {
    try {
      const base = {
        name: '',
        unit: 'lb',
        description: '',
        notes: '',
        ingredients: [{ name: '', weight: null }],
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
      };
      const ref = await addDoc(collection(firestore, 'recipes'), base);
      setRecipeId(ref.id);
      setName('');
      setUnit('lb');
      setDescription('');
      setNotes('');
      setIngredients([{ name: '', weight: '' }]);
      setStatus(`Started new recipe (id: ${ref.id})`);
      // refresh list so new doc is selectable immediately
      const snap = await getDocs(query(collection(firestore, 'recipes'), orderBy('updatedAt', 'desc')));
      setRecipesList(snap.docs.map(d => ({ id: d.id, ...(d.data() || {}) })));
    } catch (e) {
      setStatus('Error creating new recipe: ' + (e?.message || String(e)));
    }
  };

  const saveRecipe = async () => {
    setStatus('Saving...');
    try {
      const cleaned = removeEmptyIngredients(ingredients).map(i => ({
        name: i.name.trim(),
        weight: i.weight === '' ? null : Number(i.weight)
      }));

      const docData = {
        name: name.trim(),
        unit,
        description: description.trim(),
        notes: notes.trim(),
        // Always include ingredients, at least one blank row
        ingredients: cleaned.length ? cleaned : [{ name: '', weight: null }],
        updatedAt: serverTimestamp(),
      };

      let id = recipeId;
      if (id) {
        await updateDoc(doc(firestore, 'recipes', id), docData);
      } else {
        const ref = await addDoc(collection(firestore, 'recipes'), {
          ...docData,
          createdAt: serverTimestamp(),
        });
        id = ref.id;
        setRecipeId(id);
      }

      const idText = id != null && id !== '' ? ` (id: ${id})` : '';
      const nameText = name.trim();
      setStatus(`Saved${nameText ? `: ${nameText}` : ''}${idText}`);
      // refresh list
      const snap = await getDocs(query(collection(firestore, 'recipes'), orderBy('updatedAt', 'desc')));
      setRecipesList(snap.docs.map(d => ({ id: d.id, ...(d.data() || {}) })));
    } catch (e) {
      setStatus('Error: ' + (e?.message || String(e)));
    }
  };

  const loadRecipe = async (id) => {
    try {
      const d = await getDoc(doc(firestore, 'recipes', id));
      if (!d.exists()) return;
      const r = d.data();
      setRecipeId(d.id);
      setName(r.name || '');
      setUnit(r.unit || 'lb');
      setDescription(r.description || '');
      setNotes(r.notes || '');
      setIngredients((Array.isArray(r.ingredients) && r.ingredients.length ? r.ingredients : [{ name: '', weight: '' }]).map(i => ({
        name: i.name || '',
        weight: (i.weight ?? '')
      })));
      const displayName = (r.name ?? '').toString().trim();
      setStatus(displayName ? `Loaded: ${displayName}` : `Loaded recipe ${d.id}`);
    } catch (e) {
      setStatus('Load error: ' + (e?.message || String(e)));
    }
  };

  // A simple read-only preview of the current recipe (matches "display information" requirement)
  const Preview = () => (
    <div className="preview">
      <h3>Preview</h3>
      <div className="grid">
        <div><strong>Name:</strong></div><div>{name || '-'}</div>
        <div><strong>Unit:</strong></div><div>{unit}</div>
        <div><strong>Description:</strong></div><div>{description || '-'}</div>
        <div><strong>Notes:</strong></div><div>{notes || '-'}</div>
      </div>
      <div className="ingredients-preview">
        <div className="ing-header"><span>Ingredient</span><span>WT</span></div>
        {removeEmptyIngredients(ingredients).map((i, idx) => (
          <div key={idx} className="ing-row"><span>{i.name}</span><span>{i.weight}</span></div>
        ))}
        {removeEmptyIngredients(ingredients).length === 0 && <div className="ing-row empty">No ingredients</div>}
      </div>
    </div>
  );

  return (
    <div className="app-shell">
      {/* Top bar */}
      <div className="topbar">
        <div className="brand">Ratio Recipes</div>
        <div className="actions">
          <select
            aria-label="Select recipe"
            onChange={(e) => e.target.value && loadRecipe(e.target.value)}
            defaultValue=""
          >
            <option value="" disabled>Load Recipe…</option>
            {recipesList.map(r => (
              <option key={r.id} value={r.id}>{r.name || r.id}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Content */}
      <div className="container">
        <h2 className="title">View/Change Recipe</h2>

        <div className="form-grid">
          {/* Name */}
          <label className="label">Recipe Name</label>
          <input className="input" type="text" value={name} onChange={(e) => setName(e.target.value)} />

          {/* Units */}
          <label className="label">Units</label>
          <div className="units-row">
            <select className="input" value={unit} onChange={(e) => setUnit(e.target.value)}>
              <option value="g">g</option>
              <option value="kg">kg</option>
              <option value="lb">lb</option>
              <option value="oz">oz</option>
            </select>
          </div>

          {/* Description */}
          <label className="label">Description</label>
          <textarea className="input" rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />

          {/* Ingredients */}
          <label className="label">Ingredients</label>
          <div className="ingredients">
            <div className="ingredients-table">
              <div className="head">
                <span>Ingredient</span>
                <span>weight</span>
              </div>
              {ingredients.map((ing, idx) => (
                <div className="row" key={idx}>
                  <input
                    className="cell"
                    type="text"
                    value={ing.name}
                    onChange={(e) => updateIngredient(idx, 'name', e.target.value)}
                    placeholder="Ingredient Name"
                  />
                  <input
                    className="cell wt"
                    type="number"
                    step="any"
                    value={ing.weight}
                    onChange={(e) => updateIngredient(idx, 'weight', e.target.value)}
                    placeholder="weight"
                  />
                </div>
              ))}
            </div>
            <button className="add-btn" onClick={addIngredientRow}>+</button>
          </div>

          {/* Notes */}
          <label className="label">Notes</label>
          <textarea className="input" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>

        <div className="actions-row">
          <button className="btn" onClick={saveRecipe}>Update</button>
          <button className="btn" onClick={createRecipeFromScratch} style={{ marginLeft: 8 }}>Recipe from Scratch</button>
        </div>

        {status && <div className="status">{status}</div>}

        <Preview />
      </div>
    </div>
  );
}

export default App;
