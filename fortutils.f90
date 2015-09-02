subroutine get_grid_dimensions(nj, nk, nspec)
  integer, intent(in)  :: nspec
  integer, intent(out) :: nj, nk

  if(nspec.le.1) then
    open(unit=111, form='unformatted', file='fort.9')
    read(111) nj, nk
    close(111)
  else
    open(unit=111, form='unformatted', file='fort_TS1.9')
    read(111) nj, nk
    close(111)
  end if
end subroutine get_grid_dimensions

subroutine read_grid(nj, nk, x, y, nspec)
  implicit none
  integer, intent(in) :: nj, nk, nspec
  real(kind=8), dimension(nj,nk,nspec), intent(out) :: x, y

  integer :: j, k,nsp
  character(len=60) :: int_str,gfile

  if(nspec.le.1) then
    open(unit=111, form='unformatted', file='fort.9')
    read(111) j, k
    read(111) ((x(j,k,1), j=1,nj), k=1,nk), ((y(j,k,1), j=1,nj), k=1,nk)
    close(111)
  else
    do nsp=1,nspec
      write(int_str,"(i7)")nsp
      gfile='fort_TS'//trim(adjustl(int_str))//'.9'
      open(unit=111, form='unformatted', file=gfile)
      read(111) j, k
      read(111) ((x(j,k,nsp), j=1,nj), k=1,nk), ((y(j,k,nsp), j=1,nj), k=1,nk)
      close(111)
    enddo
  endif
end subroutine read_grid

subroutine read_reystress(nj,nk,x,y,u,v,uv,nspec)
  implicit none
  integer, intent(in) :: nj, nk, nspec
  real(kind=8), dimension(nj,nk,nspec), intent(out) :: x, y, u, v, uv

  integer :: i, j, nsp
  character(len=60) :: int_str,gfile


  if(nspec.le.1) then
    open(unit=111, form='unformatted', file='reystress.g')
    read(111) i, j
    read(111) ((x(i,j,1), i=1,nj), j=1,nk)
    read(111) ((y(i,j,1), i=1,nj), j=1,nk)
    read(111) ((u(i,j,1), i=1,nj), j=1,nk)
    read(111) ((v(i,j,1), i=1,nj), j=1,nk)
    read(111) ((uv(i,j,1), i=1,nj), j=1,nk)
    close(111)
  else
    do nsp=1,nspec
      write(int_str,"(i7)")nsp
      gfile='reystress_TS'//trim(adjustl(int_str))//'.g'

      open(unit=111, form='unformatted', file=gfile)
      read(111) i, j
      read(111) ((x(i,j,nsp), i=1,nj), j=1,nk)
      read(111) ((y(i,j,nsp), i=1,nj), j=1,nk)
      read(111) ((u(i,j,nsp), i=1,nj), j=1,nk)
      read(111) ((v(i,j,nsp), i=1,nj), j=1,nk)
      read(111) ((uv(i,j,nsp), i=1,nj), j=1,nk)
      close(111)
    enddo
  endif
end subroutine read_reystress


subroutine read_saadjoint(nj, nk, nspec, psi_sa)
  implicit none
  integer, intent(in) :: nj, nk, nspec
  real(kind=8), dimension(nj,nk,nspec), intent(out) :: psi_sa

  integer :: i, j, nsp
  character(len=32) :: arg
  character(len=60) :: int_str,gfile

  if(nspec.le.1) then
  
    open(111, file='SAadj.dat', form='formatted')
    do i=1, 5
       read(111, *) arg
    enddo
    read(111, *) ((psi_sa(i,j,1), i=1,nj), j=1,nk)
    read(111, *) ((psi_sa(i,j,1), i=1,nj), j=1,nk)
    read(111, *) ((psi_sa(i,j,1), i=1,nj), j=1,nk)
    read(111, *) ((psi_sa(i,j,1), i=1,nj), j=1,nk)
    close(111)
  else
    do nsp=1,nspec
      write(int_str,"(i7)")nsp
      gfile='SAadj_TS'//trim(adjustl(int_str))//'.dat'

      open(111, file=gfile, form='formatted')
      do i=1, 5
         read(111, *) arg
      enddo
      read(111, *) ((psi_sa(i,j,nsp), i=1,nj), j=1,nk)
      read(111, *) ((psi_sa(i,j,nsp), i=1,nj), j=1,nk)
      read(111, *) ((psi_sa(i,j,nsp), i=1,nj), j=1,nk)
      read(111, *) ((psi_sa(i,j,nsp), i=1,nj), j=1,nk)
      close(111)
    enddo

  endif
end subroutine read_saadjoint

subroutine read_production(nj,nk,nspec,prod)
  implicit none
  integer, intent(in) :: nj, nk, nspec
  real(kind=8), dimension(nj,nk,nspec), intent(out) :: prod

  integer :: i, j, nsp
  character(len=60) :: int_str,gfile

  if(nspec.le.1) then
    open(unit=111, form='unformatted', file='production.dat')
    read(111) i, j
    read(111) ((prod(i,j,1), i=1,nj), j=1,nk)
    close(111)
  else
    do nsp=1,nspec
      write(int_str,"(i7)")nsp
      gfile='production_TS'//trim(adjustl(int_str))//'.dat'

      open(unit=111, form='unformatted', file=gfile)
      read(111) i, j
      read(111) ((prod(i,j,nsp), i=1,nj), j=1,nk)
      close(111)
    enddo
  endif
end subroutine read_production


subroutine read_destruction(nj,nk,nspec,prod)
  implicit none
  integer, intent(in) :: nj, nk, nspec
  real(kind=8), dimension(nj,nk,nspec), intent(out) :: prod

  integer :: i, j, nsp
  character(len=60) :: int_str,gfile

  
  if(nspec.le.1) then
    open(unit=111, form='unformatted', file='destruction.dat')
    read(111) i, j
    read(111) ((prod(i,j,1), i=1,nj), j=1,nk)
    close(111)
  else
    do nsp=1,nspec
      write(int_str,"(i7)")nsp
      gfile='destruction_TS'//trim(adjustl(int_str))//'.dat'

      open(unit=111, form='unformatted', file=gfile)
      read(111) i, j
      read(111) ((prod(i,j,nsp), i=1,nj), j=1,nk)
      close(111)
    enddo
  endif
end subroutine read_destruction
subroutine get_sarc(ni,nj,sarc)
  implicit none
  integer, intent(in) :: ni, nj
  real(kind=8), dimension(ni,nj), intent(out) :: sarc

  integer :: i, j

  open(unit=111, form='unformatted', file='sarc.dat')
  read(111) i, j
  read(111) ((sarc(i,j), i=1,ni), j=1,nj)
  close(111)
end subroutine get_sarc
