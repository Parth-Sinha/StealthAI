import React from 'react';

const Loader = () => {
  return (
    <div
      className="w-40 h-10 aspect-square left-1/2 top-1/2 transform- translate-y-1/2 transform -translate-x-1/2"
      style={{
        background: `
          radial-gradient(farthest-side,#000 90%,#0000) 50%/8px 8px no-repeat,
          conic-gradient(from -90deg at 15px 15px,#0000 90deg,#fff 0) 0 0/25px 25px`,
        animation: 'l7 1s infinite',
        position: 'absolute',
      }}
    >
      <style>
        {`
          @keyframes l7 {
            0%   {background-position:50%,0 0}
            50%  {background-position:50%,25px 0}
            100% {background-position:50%,25px 25px}
          }
        `}
      </style>
    </div>
  );
};

export default Loader;
