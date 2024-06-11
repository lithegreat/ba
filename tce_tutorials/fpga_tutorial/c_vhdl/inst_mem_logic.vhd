library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use work.tta0_imem_image.all;

entity inst_mem_logic is
  
  generic (
    addrw  : integer := 10;
    instrw : integer := 100);

  port (
    clock   : in  std_logic;
    addr    : in  std_logic_vector(addrw-1 downto 0);
    dataout : out std_logic_vector(instrw-1 downto 0));

end inst_mem_logic;

architecture rtl of inst_mem_logic is
  
  subtype imem_index is integer range 0 to imem_array'length-1;
  constant imem : std_logic_imem_matrix(0 to imem_array'length-1) := imem_array;
  
begin  -- rtl

  process
    variable imem_line : imem_index;
  begin  -- process
    wait until clock'event and clock='1';
    imem_line := conv_integer(unsigned(addr));
    dataout <= imem(imem_line);
  end process;

end rtl;
