import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import api from "../api/axios";

export default function ManualPayment() {

  const { orderId } = useParams();
  const navigate = useNavigate();

  const [order, setOrder] = useState(null);
  const [file, setFile] = useState(null);

  /* GET ORDER INFO */
  useEffect(() => {
    api.get(`/orders/${orderId}`)
      .then(res => setOrder(res.data))
      .catch(() => {
        alert("Order not found");
        navigate("/");
      });
  }, [orderId, navigate]);

  const uploadProof = async () => {
    if (!file) {
      alert("Please upload payment screenshot");
      return;
    }

    const formData = new FormData();
    formData.append("screenshot", file);

    try {
      await api.post(`/payment/upload-proof/${orderId}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      alert("Payment submitted! Approval may take 5-30 minutes.");
      navigate("/purchases");

    } catch (err) {
      console.log(err);
      alert("Upload failed");
    }
  };

  if (!order) return <div className="text-white p-10">Loading...</div>;

  return (
    <div className="min-h-screen bg-[#0a0614] text-white flex flex-col items-center pt-16">

      <h1 className="text-3xl font-bold mb-4">Complete Your Payment</h1>

      <p className="mb-6 text-gray-300">
        Pay this exact amount:
        <span className="text-yellow-400 font-bold text-xl"> ₹{order.total_amount}</span>
      </p>

      <img
        src="/payment/upi.png"
        alt="UPI QR"
        className="w-72 rounded-xl border-2 border-yellow-400 mb-6"
      />

      <p className="text-gray-400 mb-6 text-center max-w-md">
        Scan QR using Google Pay / PhonePe / Paytm.  
        After payment upload screenshot below.  
        Approval time: <b>5–30 minutes (9AM–10PM IST)</b>
      </p>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />

      <button
        onClick={uploadProof}
        className="px-8 py-3 bg-yellow-400 text-black rounded-lg font-bold hover:scale-105 transition"
      >
        Upload Payment Screenshot
      </button>

    </div>
  );
}