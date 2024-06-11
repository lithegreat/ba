library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use work.tta0_imem_mau.all;
use work.tta0_imem_image.all;
use work.tta0_params.all;
use work.tta0_globals.all;

entity tutorial_processor2 is

  port (
    clk  : in  std_logic;
    rstx : in  std_logic;
    leds : out std_logic_vector(fu_leds_led_count-1 downto 0)
    );

end tutorial_processor2;

architecture structural of tutorial_processor2 is

  component tta0
    port (
      clk                : in  std_logic;
      rstx               : in  std_logic;
      busy               : in  std_logic;
      imem_en_x          : out std_logic;
      imem_addr          : out std_logic_vector(IMEMADDRWIDTH-1 downto 0);
      imem_data          : in  std_logic_vector(IMEMWIDTHINMAUS*IMEMMAUWIDTH-1 downto 0);
      fu_lsu_data_in     : in  std_logic_vector(fu_lsu_dataw-1 downto 0);
      fu_lsu_data_out    : out std_logic_vector(fu_lsu_dataw-1 downto 0);
      fu_lsu_addr        : out std_logic_vector(fu_lsu_addrw-2-1 downto 0);
      fu_lsu_mem_en_x    : out std_logic_vector(0 downto 0);
      fu_lsu_wr_en_x     : out std_logic_vector(0 downto 0);
      fu_lsu_bytemask    : out std_logic_vector(fu_lsu_dataw/8-1 downto 0);
      fu_leds_led_output : out std_logic_vector(fu_leds_led_count-1 downto 0));
  end component;

  component inst_mem_logic
    generic (
      addrw  : integer := 10;
      instrw : integer := 100);
    port (
      clock   : in  std_logic;
      addr    : in  std_logic_vector(addrw-1 downto 0);
      dataout : out std_logic_vector(instrw-1 downto 0));
  end component;

  -----------------------------------------------------------------------------
  -- put you data memory component declaration here
  -----------------------------------------------------------------------------



  -- wires for top level signals
  signal clk_w  : std_logic;
  signal rstx_w : std_logic;
  signal leds_w : std_logic_vector(fu_leds_led_count-1 downto 0);

  -- instruction memory related signals
  signal imem_addr_w : std_logic_vector(IMEMADDRWIDTH-1 downto 0);
  signal imem_data_w : std_logic_vector(IMEMWIDTHINMAUS*IMEMMAUWIDTH-1 downto 0);

  -- wires to connect TTA core to data memory component
  signal fu_lsu_data_in_w  : std_logic_vector(fu_lsu_dataw-1 downto 0);
  signal fu_lsu_data_out_w : std_logic_vector(fu_lsu_dataw-1 downto 0);
  signal fu_lsu_addr_w     : std_logic_vector(fu_lsu_addrw-2-1 downto 0);
  signal fu_lsu_mem_en_x_w : std_logic;
  signal fu_lsu_wr_en_x_w  : std_logic;
  signal fu_lsu_bytemask_w : std_logic_vector(fu_lsu_dataw/8-1 downto 0);


begin  -- structural

  clk_w     <= clk;
  rstx_w    <= rstx;

  leds <= leds_w;

  imem : inst_mem_logic
    generic map (
      addrw  => IMEMADDRWIDTH,
      instrw => IMEMWIDTHINMAUS*IMEMMAUWIDTH)
    port map (
      clock   => clk_w,
      addr    => imem_addr_w,
      dataout => imem_data_w);

  -- If your synthesis tool doesn't allow open signals, connect the open
  -- signals to dummy signals.
  core : tta0
    port map (
      clk                => clk_w,
      rstx               => rstx_w,
      busy               => '0',
      imem_en_x          => open,
      imem_addr          => imem_addr_w,
      imem_data          => imem_data_w,
      fu_lsu_data_in     => fu_lsu_data_in_w,
      fu_lsu_data_out    => fu_lsu_data_out_w,
      fu_lsu_addr        => fu_lsu_addr_w,
      fu_lsu_mem_en_x(0) => fu_lsu_mem_en_x_w,
      fu_lsu_wr_en_x(0)  => fu_lsu_wr_en_x_w,
      fu_lsu_bytemask    => fu_lsu_bytemask_w,
      fu_leds_led_output => leds_w);

  -----------------------------------------------------------------------------
  -- Connect data memory component here.  Notice that you may need to invert
  -- enable signals! (enable signals from lsu are active low)
  -----------------------------------------------------------------------------



end structural;
