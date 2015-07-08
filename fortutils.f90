subroutine get_grid_dimensions(nj, nk)
  integer, intent(out) :: nj, nk
  open(unit=111, form='unformatted', file='fort.9')
  read(111) nj, nk
  close(111)
end subroutine get_grid_dimensions

subroutine read_grid(nj, nk, x, y)
  implicit none
  integer, intent(in) :: nj, nk
  real(kind=8), dimension(nj,nk), intent(out) :: x, y
  integer :: j, k
  open(unit=111, form='unformatted', file='fort.9')
  read(111) j, k
  read(111) ((x(j,k), j=1,nj), k=1,nk), ((y(j,k), j=1,nj), k=1,nk)
  close(111)
end subroutine read_grid

subroutine read_reystress(nj,nk,x,y,u,v,uv)
  implicit none
  integer, intent(in) :: nj, nk
  real(kind=8), dimension(nj,nk), intent(out) :: x, y, u, v, uv

  integer :: i, j

  open(unit=111, form='unformatted', file='reystress.g')
  read(111) i, j
  read(111) ((x(i,j), i=1,nj), j=1,nk)
  read(111) ((y(i,j), i=1,nj), j=1,nk)
  read(111) ((u(i,j), i=1,nj), j=1,nk)
  read(111) ((v(i,j), i=1,nj), j=1,nk)
  read(111) ((uv(i,j), i=1,nj), j=1,nk)
  close(111)
end subroutine read_reystress


subroutine read_saadjoint(nj, nk, psi_sa)
  implicit none
  integer, intent(in) :: nj, nk
  real(kind=8), dimension(nj,nk), intent(out) :: psi_sa

  integer :: i, j
  character(len=32) :: arg

  open(111, file='SAadj.dat', form='formatted')
  do i=1, 5
     read(111, *) arg
  enddo
  read(111, *) ((psi_sa(i,j), i=1,nj), j=1,nk)
  read(111, *) ((psi_sa(i,j), i=1,nj), j=1,nk)
  read(111, *) ((psi_sa(i,j), i=1,nj), j=1,nk)
  read(111, *) ((psi_sa(i,j), i=1,nj), j=1,nk)
  close(111)
end subroutine read_saadjoint

subroutine read_production(nj,nk,prod)
  implicit none
  integer, intent(in) :: nj, nk
  real(kind=8), dimension(nj,nk), intent(out) :: prod

  integer :: i, j

  open(unit=111, form='unformatted', file='production.dat')
  read(111) i, j
  read(111) ((prod(i,j), i=1,nj), j=1,nk)
  close(111)
end subroutine read_production
