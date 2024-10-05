import React, { useState, useEffect } from 'react';
import { Container, Form, ListGroup, Alert } from 'react-bootstrap';
import FundDetails from './FundDetails';

const Dashboard = () => {
  const [selectedFamily, setSelectedFamily] = useState('');
  const [schemes, setSchemes] = useState([]);
  const [purchasedFunds, setPurchasedFunds] = useState([]);
  const [fundFamilies, setFundFamilies] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // fetch token from local storage
  const token = localStorage.getItem('token');

  // function to fetch fund families from the backend
  const fetchFundFamilies = async () => {
    try {
      const response = await fetch('http://localhost:8000/fund_families', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorMessage = await response.json();
        throw new Error(errorMessage.detail || 'Failed to fetch fund families');
      }

      const data = await response.json();
      setFundFamilies(data.families);
    } catch (err) {
      setError(err.message);
    }
  };

  // function to fetch schemes from the backend
  const fetchSchemes = async (familyId) => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(`http://localhost:8000/funds/${familyId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorMessage = await response.json();
        throw new Error(errorMessage.detail || 'Failed to fetch schemes');
      }

      const data = await response.json();
      setSchemes(data); 
    } catch (err) {
      setError(err.message);
      setSchemes([]);
    } finally {
      setLoading(false);
    }
  };

  // function to fetch purchased funds
  const fetchPurchasedFunds = async () => {
    try {
      const response = await fetch('http://localhost:8000/funds/purchases', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorMessage = await response.json();
        throw new Error(errorMessage.detail || 'Failed to fetch purchased funds');
      }

      const data = await response.json();
      setPurchasedFunds(data);
    } catch (err) {
      setError(err.message);
    }
  };

  // function to update prices of purchased funds
  const updatePurchasedFundsPrices = async () => {
    for (const fund of purchasedFunds) {
      try {
        const response = await fetch(`http://localhost:8000/funds/fetch_scheme_value?scheme=${fund.scheme_name}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          const errorMessage = await response.json();
          throw new Error(errorMessage.detail || 'Failed to fetch scheme value');
        }

        const currentValue = await response.json();
        setPurchasedFunds(prev => 
          prev.map(f => 
            f.scheme_name === fund.scheme_name ? { ...f, value: currentValue.value } : f
          )
        );
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const handleFamilySelect = (e) => {
    const familyId = e.target.value;
    setSelectedFamily(familyId);
    if (familyId) {
      fetchSchemes(familyId);
    } else {
      setSchemes([]);
    }
  };

  // function to handle buying a mutual fund
  const handleBuy = async (scheme) => {
    try {
      const response = await fetch('http://localhost:8000/funds/purchase', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ scheme_code: scheme.Scheme_Code, units: 1 }) 
      });

      if (!response.ok) {
        const errorMessage = await response.json();
        throw new Error(errorMessage.detail || 'Failed to purchase fund');
      }

      const result = await response.json();
      alert(result.message);
      fetchPurchasedFunds(); 
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  // fetch purchased funds and fund families on component mount
  useEffect(() => {
    fetchFundFamilies();
    fetchPurchasedFunds();
  }, []);

  // polling to update purchased funds prices every hour
  useEffect(() => {
    const interval = setInterval(() => {
      updatePurchasedFundsPrices();
    }, 3600000); 

    return () => clearInterval(interval); // cleanup on unmount
  }, [purchasedFunds]);

  return (
    <Container className="mt-5">
      <h2>Dashboard</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      {loading && <Alert variant="info">Loading schemes...</Alert>}

      <Form.Group controlId="formFundFamily">
        <Form.Label>Select Fund Family</Form.Label>
        <Form.Select onChange={handleFamilySelect} value={selectedFamily}>
          <option value="">Select Family</option>
          {fundFamilies.map((family) => (
            <option key={family} value={family}>
              {family}
            </option>
          ))}
        </Form.Select>
      </Form.Group>

      {schemes.length > 0 && (
        <ListGroup className="mt-3">
          {schemes.map((scheme, idx) => (
            <ListGroup.Item key={scheme.Scheme_Code}>
              <FundDetails scheme={scheme} onBuy={handleBuy} />
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}

      {/* Purchased Funds Section */}
      {purchasedFunds.length > 0 && (
        <div className="mt-5">
          <h3>Purchased Funds</h3>
          <ListGroup>
            {purchasedFunds.map((fund, idx) => (
              <ListGroup.Item key={idx}>
                {fund.scheme_name} - {fund.units} units @ ${fund.value.toFixed(2)}
              </ListGroup.Item>
            ))}
          </ListGroup>
        </div>
      )}
    </Container>
  );
};

export default Dashboard;
