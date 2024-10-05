import React from 'react';
import { Button } from 'react-bootstrap';

const FundDetails = ({ scheme, onBuy }) => {
  return (
    <div className="d-flex justify-content-between align-items-center">
      <span>{scheme}</span>
      <Button variant="success" onClick={() => onBuy(scheme)}>
        Buy
      </Button>
    </div>
  );
};

export default FundDetails;
