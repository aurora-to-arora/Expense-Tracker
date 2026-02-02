import { useState, useEffect } from "react";
import "./styles.css";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [form, setForm] = useState({
    amount: "",
    category: "",
    description: "",
    date: "",
  });
  const [filterCategory, setFilterCategory] = useState("");
  const [sortNewest, setSortNewest] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchExpenses = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = `${API_BASE}/expenses?`;
      if (filterCategory) url += `category=${filterCategory}&`;
      if (sortNewest) url += `sort=date_desc`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch expenses");
      const data = await res.json();
      setExpenses(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenses();
  }, [filterCategory, sortNewest]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!form.amount || !form.category || !form.date) {
      setError("Amount, category, and date are required.");
      return;
    }
    const selectedDate = new Date(form.date);
    const today = new Date();
    today.setHours(0, 0, 0, 0); 
    if (selectedDate > today) {
      setError("Date cannot be in the future.");
      return;
    }
    const payload = { ...form, amount: parseFloat(form.amount) };
    const idempotencyKey = crypto.randomUUID();

    try {
      const res = await fetch(`${API_BASE}/expenses`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey,
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Failed to add expense");

      setForm({ amount: "", category: "", description: "", date: "" });
      fetchExpenses();
    } catch (err) {
      setError(err.message);
    }
  };

   const filteredExpenses = expenses.filter((exp) =>
    exp.category.toLowerCase().includes(filterCategory.toLowerCase())
  );

  const totalAmount = filteredExpenses.reduce((acc, e) => acc + e.amount, 0);
 

  return (
    <div className="container">
      <h1>Expense Tracker</h1>

      <form onSubmit={handleSubmit} className="expense-form">
        <input
          type="number"
          step="0.01"
          placeholder="Amount"
          value={form.amount}
          onChange={(e) => setForm({ ...form, amount: e.target.value })}
        />
        <input
          type="text"
          placeholder="Category"
          value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}
        />
        <input
          type="text"
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <input
          type="date"
          value={form.date}
          onChange={(e) => setForm({ ...form, date: e.target.value })}
        />
        <button type="submit">Add Expense</button>
      </form>

      {error && <p className="error">{error}</p>}

      <div className="controls">
        <input
          type="text"
          placeholder="Filter by category"
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        />
        <label>
          <input
            type="checkbox"
            checked={sortNewest}
            onChange={(e) => setSortNewest(e.target.checked)}
          />
          Sort by newest
        </label>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="table-container">
          <table className="expense-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Amount</th>
                <th>Category</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {filteredExpenses.map((exp) => (
                <tr key={exp.id}>
                  <td>{exp.date}</td>
                  <td>₹{exp.amount.toFixed(2)}</td>
                  <td>{exp.category}</td>
                  <td>{exp.description || "-"}</td>
              </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h3 className="total">Total: ₹{totalAmount.toFixed(2)}</h3>
    </div>
  );
}
